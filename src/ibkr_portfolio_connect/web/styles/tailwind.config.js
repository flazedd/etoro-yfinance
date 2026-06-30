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
  // diagnostics.html builds class names at render time (bg-{{c}}-100 etc.) that
  // the static scanner can't see; the JIT CDN used to generate these in-browser.
  safelist: [{ pattern: /(bg|text)-(emerald|amber|rose|slate)-(100|500|700)/ }],
  theme: { extend: {} },
  plugins: [],
};
