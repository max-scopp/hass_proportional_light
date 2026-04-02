/**
 * Entry point for the Proportional Light frontend panel bundle.
 *
 * Registers all custom elements. HA loads this file once via panel_custom
 * and the elements become available on the global custom element registry.
 */

import "./panel.js";
import "./components/entry-editor.js";

// eslint-disable-next-line no-console
console.info(
    "%c PROPORTIONAL-LIGHT %c panel loaded",
    "background:#1565c0;color:#fff;padding:2px 6px;border-radius:3px 0 0 3px;font-weight:bold",
    "background:#333;color:#1565c0;padding:2px 6px;border-radius:0 3px 3px 0"
);
