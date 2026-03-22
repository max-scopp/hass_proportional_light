/**
 * Minimal type definitions for the Home Assistant `hass` object.
 * These mirror the shapes exposed by home-assistant-js-websocket and HA's
 * internal frontend — extend as needed rather than pulling in the whole HA
 * frontend package as a dependency.
 */

export interface HassEntityAttributes {
    friendly_name?: string;
    supported_color_modes?: string[];
    brightness?: number;
    hs_color?: [number, number];
    color_temp_kelvin?: number;
    min_color_temp_kelvin?: number;
    max_color_temp_kelvin?: number;
    [key: string]: unknown;
}

export interface HassEntity {
    entity_id: string;
    state: string;
    attributes: HassEntityAttributes;
    last_changed: string;
    last_updated: string;
    context: { id: string; user_id: string | null; parent_id: string | null };
}

export interface HassConfig {
    location_name: string;
    time_zone: string;
    components: string[];
}

export interface HassUser {
    id: string;
    name: string;
    is_admin: boolean;
    is_owner: boolean;
}

export interface HomeAssistant {
    states: Record<string, HassEntity>;
    config: HassConfig;
    user: HassUser;
    language: string;
    localize: (key: string, ...args: unknown[]) => string;
    callWS: <T = unknown>(message: Record<string, unknown>) => Promise<T>;
    callService: (
        domain: string,
        service: string,
        serviceData?: Record<string, unknown>,
        target?: Record<string, unknown>
    ) => Promise<void>;
    connection: {
        sendMessagePromise: <T>(message: Record<string, unknown>) => Promise<T>;
        addEventListener: (event: string, cb: (conn: unknown, event: unknown) => void) => void;
    };
}

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

export type SelectorType = "entities" | "area" | "device";

export interface EntityProps {
    hue_offset?: number;
    default_proportion?: number;
}

export interface EntryData {
    /** Human-readable name set during initial config flow. */
    name: string;
    /** How entities are selected for this group. */
    selector_type: SelectorType;
    /**
     * The selector value:
     *   entities → string[]
     *   area     → string  (area_id)
     *   device   → string  (device_id)
     */
    selector_value: string | string[];
    /** Per-entity overrides, keyed by entity_id. */
    entity_props: Record<string, EntityProps>;
    /** When to reset stored brightness proportions. */
    proportion_reset_mode: string;
    /** Seconds after last turn-off before proportions reset (when mode = timeout). */
    proportion_reset_timeout: number;
}

export interface ConfigEntry {
    entry_id: string;
    title: string;
    domain: string;
    state: string;
    source: string;
    data: EntryData;
    options: Partial<EntryData>;
}

// ---------------------------------------------------------------------------
// WS response shapes
// ---------------------------------------------------------------------------

export interface ResolvedEntitiesResponse {
    entities: string[];
}
