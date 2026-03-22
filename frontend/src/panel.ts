import { LitElement, html, css, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import type { ConfigEntry, HomeAssistant } from "./types.js";

/**
 * Top-level panel element registered as <proportional-light-panel>.
 *
 * HA mounts this element when the user navigates to the custom panel URL
 * registered via panel_custom.async_register_panel in __init__.py.
 *
 * The element lists all proportional_light config entries and lets the user
 * open an editor for each one.
 */
@customElement("proportional-light-panel")
export class ProportionalLightPanel extends LitElement {
    @property({ attribute: false }) hass!: HomeAssistant;
    @property({ type: Boolean }) narrow = false;
    @property({ attribute: false }) route: unknown = null;

    @state() private _entries: ConfigEntry[] = [];
    @state() private _loading = true;
    @state() private _error: string | null = null;
    @state() private _editingEntryId: string | null = null;

    // -------------------------------------------------------------------------
    // Lifecycle
    // -------------------------------------------------------------------------

    connectedCallback(): void {
        super.connectedCallback();
        this._loadEntries();
    }

    // -------------------------------------------------------------------------
    // Data loading
    // -------------------------------------------------------------------------

    private async _loadEntries(): Promise<void> {
        this._loading = true;
        this._error = null;
        try {
            // HA's standard WS command — returns all entries for this domain
            const entries = await this.hass.callWS<ConfigEntry[]>({
                type: "config_entries/get",
                domain: "proportional_light",
            });
            this._entries = entries;
        } catch (err) {
            this._error = String(err);
        } finally {
            this._loading = false;
        }
    }

    // -------------------------------------------------------------------------
    // Render
    // -------------------------------------------------------------------------

    render() {
        return html`
      <hass-subpage
        .hass=${this.hass}
        .narrow=${this.narrow}
        header="Proportional Light Groups"
      >
        <ha-fab
          slot="fab"
          label="Add group"
          extended
          @click=${this._handleAdd}
        >
          <ha-icon slot="icon" icon="mdi:plus"></ha-icon>
        </ha-fab>

        <div class="content">
          ${this._loading
                ? html`<div class="loading">
                <ha-circular-progress active></ha-circular-progress>
              </div>`
                : this._error
                    ? html`<ha-alert alert-type="error">${this._error}</ha-alert>`
                    : this._entries.length === 0
                        ? html`<div class="empty">
                <p>No proportional light groups configured yet.</p>
                <p>Click + to create your first group.</p>
              </div>`
                        : this._renderEntries()}
        </div>
      </hass-subpage>
    `;
    }

    private _renderEntries() {
        return html`
      ${this._entries.map(
            (entry) => html`
          <ha-card
            class="entry-card"
            .header=${entry.title || entry.data.name || "Unnamed Group"}
          >
            <div class="card-content">
              <div class="selector-badge">
                <ha-icon icon=${this._selectorIcon(entry.data.selector_type)}></ha-icon>
                <span>${this._selectorLabel(entry.data.selector_type, entry.data.selector_value)}</span>
              </div>
              <div class="entry-state state-${entry.state}">${entry.state}</div>
            </div>
            <div class="card-actions">
              <ha-button @click=${() => this._handleEdit(entry)}>
                Configure
              </ha-button>
              <ha-button
                class="danger"
                @click=${() => this._handleDelete(entry)}
              >
                Remove
              </ha-button>
            </div>
          </ha-card>
        `
        )}
    `;
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private _selectorIcon(type: string | undefined): string {
        switch (type) {
            case "area":
                return "mdi:floor-plan";
            case "device":
                return "mdi:chip";
            default:
                return "mdi:lightbulb-multiple";
        }
    }

    private _selectorLabel(type: string | undefined, value: string | string[] | undefined): string {
        if (!value) return "—";
        switch (type) {
            case "area":
                return `Area: ${value}`;
            case "device":
                return `Device: ${value}`;
            default: {
                const list = Array.isArray(value) ? value : [value];
                return `${list.length} light${list.length !== 1 ? "s" : ""}`;
            }
        }
    }

    // -------------------------------------------------------------------------
    // Event handlers
    // -------------------------------------------------------------------------

    private _handleEdit(entry: ConfigEntry): void {
        this._editingEntryId = entry.entry_id;
        // Fire a custom event so the panel container (or router) can react
        this.dispatchEvent(
            new CustomEvent("edit-entry", { detail: { entry }, bubbles: true, composed: true })
        );
    }

    private _handleAdd(): void {
        this.dispatchEvent(
            new CustomEvent("add-entry", { bubbles: true, composed: true })
        );
    }

    private async _handleDelete(entry: ConfigEntry): Promise<void> {
        if (!confirm(`Remove "${entry.title}"? This cannot be undone.`)) return;
        try {
            await this.hass.callWS({ type: "config_entries/delete", entry_id: entry.entry_id });
            await this._loadEntries();
        } catch (err) {
            alert(`Failed to remove entry: ${err}`);
        }
    }

    // -------------------------------------------------------------------------
    // Styles
    // -------------------------------------------------------------------------

    static styles = css`
    :host {
      display: block;
    }
    .content {
      padding: 16px;
      max-width: 900px;
      margin: 0 auto;
    }
    .loading,
    .empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 16px;
      color: var(--secondary-text-color);
      text-align: center;
    }
    ha-card.entry-card {
      margin-bottom: 16px;
    }
    .card-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px 16px;
    }
    .selector-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--secondary-text-color);
      font-size: 0.9rem;
    }
    .entry-state {
      font-size: 0.75rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 2px 8px;
      border-radius: 12px;
      background: var(--divider-color);
    }
    .entry-state.state-loaded {
      background: var(--success-color);
      color: #fff;
    }
    .entry-state.state-not_loaded,
    .entry-state.state-failed_unload {
      background: var(--error-color);
      color: #fff;
    }
    .card-actions {
      display: flex;
      justify-content: flex-end;
      padding: 8px 8px 8px;
      gap: 8px;
    }
    ha-button.danger {
      --mdc-theme-primary: var(--error-color);
    }
  `;
}
