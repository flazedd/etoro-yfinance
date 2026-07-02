/** Tailwind source for the momentum-stack web UI.
 *
 * The built CSS is committed at ../static/tailwind.css so the Pi needs no
 * Node/JS toolchain at runtime. To rebuild after changing template classes:
 *
 *   # from repo root, with the standalone CLI on PATH (no node_modules needed):
 *   tailwindcss -c src/ibkr_portfolio_connect/web/styles/tailwind.config.js \
 *     -i src/ibkr_portfolio_connect/web/styles/input.css \
 *     -o src/ibkr_portfolio_connect/web/static/tailwind.css --minify
 *
 * Get the CLI binary from github.com/tailwindlabs/tailwindcss/releases
 * (tailwindcss-<os>-<arch>), or run via `npx tailwindcss@3`.
 */
// content globs resolve relative to CWD; run the rebuild from the repo root.
module.exports = {
  content: ["src/ibkr_portfolio_connect/web/templates/**/*.html"],
  // diagnostics.html + home.html build class names at render time (bg-{{c}}-100,
  // bg-{{accent}}-50 etc.) that the static scanner can't see.
  safelist: [
    { pattern: /(bg|text)-(emerald|amber|rose|slate)-(100|500|700)/ },
    // home.html accent icon-badges + hover arrow (one per section card).
    { pattern: /(bg|text)-(emerald|blue|amber|violet|rose)-(50|500|600)/, variants: ["group-hover"] },
  ],
  theme: { extend: {} },
  plugins: [],
};
