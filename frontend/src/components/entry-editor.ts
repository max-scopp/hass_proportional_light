import { LitElement, html, css, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import type {
    ConfigEntry,
    EntryData,
    EntityProps,
    HomeAssistant,
    ResolvedEntitiesResponse,
    SelectorType,
} from "../types.js";

type Selector =
    | { entity: { domain?: string; multiple?: boolean } }
    | { area: Record<string, never> }
    | { device: Record<string, never> };

/**
 * Editor element for a single proportional light config entry.
 *
 * Uses HA's built-in <ha-selector> to render the right picker depending on
 * the chosen selector_type, then lists the resolved entities for per-light
 * property overrides.
 *
 * Usage:
 *   <proportional-light-entry-editor
 *     .hass=${hass}
 *     .entry=${configEntry}
 *     @save=${handler}
 *     @cancel=${handler}
 *   ></proportional-light-entry-editor>
 */
@customElement("proportional-light-entry-editor")
export class ProportionalLightEntryEditor extends LitElement {
    @property({ attribute: false }) hass!: HomeAssistant;
    /** Existing entry to edit, or undefined when creating a new one. */
    @property({ attribute: false }) entry?: ConfigEntry;

    @state() private _name = "";
    @state() private _selectorType: SelectorType = "entities";
    @state() private _selectorValue: string | string[] | null = null;
    @state() private _entityProps: Record<string, EntityProps> = {};
    @state() private _proportionResetMode = "on_specific_brightness";
    @state() private _proportionResetTimeout = 28800;
    @state() private _resolvedEntities: string[] = [];
    @state() private _resolving = false;
    @state() private _saving = false;

    // -------------------------------------------------------------------------
    // Lifecycle
    // -------------------------------------------------------------------------

    willUpdate(changed: Map<string, unknown>): void {
        // Populate form when entry prop changes
        if (changed.has("entry") && this.entry) {
            const d = { ...this.entry.data, ...this.entry.options } as EntryData;
            this._name = d.name ?? this.entry.title ?? "";
            this._selectorType = d.selector_type ?? "entities";
            this._selectorValue = d.selector_value ?? [];
            this._entityProps = d.entity_props ?? {};
            this._proportionResetMode = d.proportion_reset_mode ?? "on_specific_brightness";
            this._proportionResetTimeout = d.proportion_reset_timeout ?? 28800;
            if (this._selectorValue) this._resolveEntities();
        }
    }

    // -------------------------------------------------------------------------
    // Entity resolution
    // -------------------------------------------------------------------------

    private async _resolveEntities(): Promise<void> {
        if (!this.entry || !this._selectorValue) {
            this._resolvedEntities = [];
            return;
        }
        this._resolving = true;
        try {
            const resp = await this.hass.callWS<ResolvedEntitiesResponse>({
                type: "proportional_light/get_resolved_entities",
                entry_id: this.entry.entry_id,
            });
            this._resolvedEntities = resp.entities;
        } catch {
            this._resolvedEntities = [];
        } finally {
            this._resolving = false;
        }
    }

    // -------------------------------------------------------------------------
    // Render
    // -------------------------------------------------------------------------

    render() {
        return html`
      <ha-card header=${this.entry ? "Edit Group" : "New Group"}>
        <div class="card-content">
          <!-- Name -->
          <ha-textfield
            label="Group name"
            .value=${this._name}
            @input=${(e: InputEvent) => (this._name = (e.target as HTMLInputElement).value)}
          ></ha-textfield>

          <!-- Selector type -->
          <div class="section-label">Entity source</div>
          <ha-select
            label="Source type"
            .value=${this._selectorType}
            @selected=${this._handleSelectorTypeChange}
            @closed=${(e: Event) => e.stopPropagation()}
          >
            <ha-list-item value="entities">Specific lights</ha-list-item>
            <ha-list-item value="area">Area</ha-list-item>
            <ha-list-item value="device">Device</ha-list-item>
          </ha-select>

          <!-- Dynamic HA selector — changes based on selected type -->
          <ha-selector
            .hass=${this.hass}
            .selector=${this._buildSelectorConfig()}
            .value=${this._selectorValue ?? (this._selectorType === "entities" ? [] : "")}
            .label=${"Select " + this._selectorType}
            @value-changed=${this._handleSelectorValueChange}
          ></ha-selector>

          <!-- Resolved entity list with per-light overrides -->
          ${this._resolvedEntities.length > 0
                ? html`
                <div class="section-label">
                  Per-light settings
                  ${this._resolving
                        ? html`<ha-circular-progress active size="small"></ha-circular-progress>`
                        : nothing}
                </div>
                ${this._renderEntityProps()}
              `
                : this._resolving
                    ? html`<ha-circular-progress active></ha-circular-progress>`
                    : nothing}

          <!-- Proportion reset -->
          <div class="section-label">Proportion reset</div>
          <ha-selector
            .hass=${this.hass}
            .selector=${{
                select: {
                    options: [
                        { value: "never", label: "Never" },
                        { value: "on_off", label: "On turn-off" },
                        { value: "on_specific_brightness", label: "When turned on with explicit brightness" },
                        { value: "on_off_and_specific", label: "Both of the above" },
                    ],
                },
            }}
            .value=${this._proportionResetMode}
            label="Reset mode"
            @value-changed=${(e: CustomEvent) => (this._proportionResetMode = e.detail.value)}
          ></ha-selector>

          <ha-selector
            .hass=${this.hass}
            .selector=${{
                number: { min: 0, max: 86400, step: 300, mode: "box", unit_of_measurement: "s" },
            }}
            .value=${this._proportionResetTimeout}
            label="Reset timeout"
            @value-changed=${(e: CustomEvent) => (this._proportionResetTimeout = Number(e.detail.value))}
          ></ha-selector>
        </div>

        <div class="card-actions">
          <ha-button @click=${this._handleCancel}>Cancel</ha-button>
          <ha-button
            raised
            .disabled=${this._saving}
            @click=${this._handleSave}
          >
            ${this._saving ? "Saving…" : "Save"}
          </ha-button>
        </div>
      </ha-card>
    `;
    }

    private _renderEntityProps() {
        return html`
      <div class="entity-list">
        ${this._resolvedEntities.map((entityId) => {
            const props = this._entityProps[entityId] ?? {};
            const state = this.hass.states[entityId];
            const label = state?.attributes?.friendly_name ?? entityId;
            const isColorable = this._isColorable(entityId);

            return html`
            <ha-card outlined class="entity-row">
              <div class="entity-row-content">
                <state-badge
                  .hass=${this.hass}
                  .stateObj=${state}
                ></state-badge>
                <div class="entity-info">
                  <div class="entity-name">${label}</div>
                  <div class="entity-id">${entityId}</div>
                </div>
                <div class="entity-controls">
                  <ha-selector
                    .hass=${this.hass}
                    .selector=${{ number: { min: 0, max: 100, step: 1, mode: "slider", unit_of_measurement: "%" } }}
                    .value=${(props.default_proportion ?? 1) * 100}
                    label="Default proportion"
                    @value-changed=${(e: CustomEvent) =>
                    this._updateEntityProp(entityId, "default_proportion", Number(e.detail.value) / 100)}
                  ></ha-selector>
                  ${isColorable
                    ? html`
                        <ha-selector
                          .hass=${this.hass}
                          .selector=${{ number: { min: -180, max: 180, step: 1, mode: "box", unit_of_measurement: "°" } }}
                          .value=${props.hue_offset ?? 0}
                          label="Hue offset"
                          @value-changed=${(e: CustomEvent) =>
                            this._updateEntityProp(entityId, "hue_offset", Number(e.detail.value))}
                        ></ha-selector>
                      `
                    : nothing}
                </div>
              </div>
            </ha-card>
          `;
        })}
      </div>
    `;
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private _buildSelectorConfig(): Selector {
        switch (this._selectorType) {
            case "area":
                return { area: {} };
            case "device":
                return { device: {} };
            default:
                return { entity: { domain: "light", multiple: true } };
        }
    }

    private _isColorable(entityId: string): boolean {
        const state = this.hass.states[entityId];
        if (!state) return false;
        const modes: string[] = (state.attributes.supported_color_modes as string[]) ?? [];
        return modes.some((m) => ["hs", "xy", "rgb", "rgbw", "rgbww"].includes(m));
    }

    private _updateEntityProp<K extends keyof EntityProps>(
        entityId: string,
        key: K,
        value: EntityProps[K]
    ): void {
        this._entityProps = {
            ...this._entityProps,
            [entityId]: { ...this._entityProps[entityId], [key]: value },
        };
    }

    // -------------------------------------------------------------------------
    // Event handlers
    // -------------------------------------------------------------------------

    private _handleSelectorTypeChange(e: CustomEvent): void {
        const newType = (e.target as HTMLSelectElement).value as SelectorType;
        if (newType === this._selectorType) return;
        this._selectorType = newType;
        // Reset value when type changes — incompatible shapes
        this._selectorValue = newType === "entities" ? [] : "";
        this._resolvedEntities = [];
    }

    private _handleSelectorValueChange(e: CustomEvent): void {
        this._selectorValue = e.detail.value;
        // Debounce: wait until a real value exists before calling WS
        if (this._selectorValue && (Array.isArray(this._selectorValue) ? this._selectorValue.length > 0 : true)) {
            this._resolveEntities();
        }
    }

    private async _handleSave(): Promise<void> {
        if (!this._name.trim()) {
            alert("Please enter a name for the group.");
            return;
        }
        if (!this._selectorValue || (Array.isArray(this._selectorValue) && this._selectorValue.length === 0)) {
            alert("Please select at least one entity source.");
            return;
        }

        this._saving = true;
        try {
            const data: EntryData = {
                name: this._name.trim(),
                selector_type: this._selectorType,
                selector_value: this._selectorValue,
                entity_props: this._entityProps,
                proportion_reset_mode: this._proportionResetMode,
                proportion_reset_timeout: this._proportionResetTimeout,
            };

            if (this.entry) {
                // Update existing entry via custom WS command
                await this.hass.callWS({
                    type: "proportional_light/update_entry",
                    entry_id: this.entry.entry_id,
                    data,
                });
            }
            // For new entries the user goes through the integration config flow;
            // this editor is therefore only used for editing existing groups.

            this.dispatchEvent(new CustomEvent("save", { detail: { data }, bubbles: true, composed: true }));
        } catch (err) {
            alert(`Save failed: ${err}`);
        } finally {
            this._saving = false;
        }
    }

    private _handleCancel(): void {
        this.dispatchEvent(new CustomEvent("cancel", { bubbles: true, composed: true }));
    }

    // -------------------------------------------------------------------------
    // Styles
    // -------------------------------------------------------------------------

    static styles = css`
    :host {
      display: block;
    }
    .card-content {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 16px;
    }
    .section-label {
      font-size: 0.85rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--secondary-text-color);
      margin-top: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    ha-textfield,
    ha-select,
    ha-selector {
      width: 100%;
    }
    .entity-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    ha-card.entity-row {
      --ha-card-border-radius: 8px;
    }
    .entity-row-content {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px;
    }
    .entity-info {
      flex: 0 0 auto;
      min-width: 160px;
    }
    .entity-name {
      font-weight: 500;
    }
    .entity-id {
      font-size: 0.8rem;
      color: var(--secondary-text-color);
    }
    .entity-controls {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .card-actions {
      display: flex;
      justify-content: flex-end;
      padding: 8px;
      gap: 8px;
      border-top: 1px solid var(--divider-color);
    }
  `;
}
