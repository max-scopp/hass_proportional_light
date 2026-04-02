# Proportional Light Frontend

Lit + TypeScript custom elements for the proportional light integration.

## Build

```bash
# One-time setup
npm install

# Production build (outputs to ../custom_components/proportional_light/www/panel.js)
npm run build

# Development with auto-rebuild on file changes
npm run dev
```

After building, restart Home Assistant to pick up the changes.

## Structure

- **`src/panel.ts`** — `<proportional-light-panel>` — groups list UI
- **`src/components/entry-editor.ts`** — `<proportional-light-entry-editor>` — edit dialog  
- **`src/types.ts`** — TypeScript interfaces for HA state & config
- **`src/index.ts`** — entry point, registers all custom elements

## Architecture

- Lit 3 + TypeScript
- Reuses HA's built-in web components (`<ha-selector>`, `<ha-card>`, `<ha-button>`, etc.) — no custom UI library
- Single bundled output: `panel.js` (~44 kB, includes Lit)
- Future: integrate as sidebar panel at `/proportional-light`
