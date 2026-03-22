import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
    build: {
        outDir: resolve(__dirname, "../custom_components/proportional_light/www"),
        emptyOutDir: true,
        lib: {
            entry: resolve(__dirname, "src/index.ts"),
            formats: ["es"],
            fileName: () => "panel.js",
        },
        rollupOptions: {
            // Everything is bundled — HA does not expose Lit or any other library
            // globally, so we include our own copy in the output.
        },
        target: "es2020",
        minify: false, // keep readable during development; enable for production
    },
});
