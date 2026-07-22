/* Click-to-sort for any <table class="sortable">. Toggles asc <-> desc on each
 * <th data-sort>; add data-type="num" for numeric columns. Cells may carry a
 * data-sort-value to sort on a value that differs from the displayed text.
 * Blanks always sink to the bottom regardless of direction. Works across HTMX
 * swaps (delegated) and re-applies the active sort after a swap. */
(function () {
  "use strict";

  function cellKey(row, idx, type) {
    var td = row.children[idx];
    if (!td) return type === "num" ? null : "";
    var raw = td.dataset.sortValue !== undefined ? td.dataset.sortValue : td.textContent.trim();
    if (type === "num") {
      if (raw === "" || raw === "—") return null;
      var n = parseFloat(String(raw).replace(/[,\s€]/g, ""));
      return isNaN(n) ? null : n;
    }
    return raw.toLowerCase();
  }

  function isBlank(v) { return v === null || v === ""; }

  function sortTable(table, idx, type, dir) {
    var tbody = table.tBodies[0];
    if (!tbody) return;
    var rows = Array.prototype.slice.call(tbody.rows);
    var mul = dir === "asc" ? 1 : -1;
    rows.sort(function (a, b) {
      var va = cellKey(a, idx, type), vb = cellKey(b, idx, type);
      var ea = isBlank(va), eb = isBlank(vb);
      if (ea && eb) return 0;
      if (ea) return 1;          // blanks last
      if (eb) return -1;
      if (va < vb) return -1 * mul;
      if (va > vb) return 1 * mul;
      return 0;
    });
    rows.forEach(function (r) { tbody.appendChild(r); });
  }

  function paintCarets(table, activeTh, dir) {
    table.querySelectorAll("th[data-sort] .caret").forEach(function (c) { c.textContent = ""; });
    var caret = activeTh.querySelector(".caret");
    if (caret) caret.textContent = dir === "asc" ? " ▲" : " ▼";
  }

  function apply(table, idx, type, dir) {
    var th = table.tHead && table.tHead.rows[0] ? table.tHead.rows[0].children[idx] : null;
    sortTable(table, idx, type, dir);
    if (th) {
      table.querySelectorAll("th[data-sort]").forEach(function (h) { delete h.dataset.dir; });
      th.dataset.dir = dir;
      paintCarets(table, th, dir);
    }
  }

  document.addEventListener("click", function (e) {
    var th = e.target.closest("th[data-sort]");
    if (!th) return;
    var table = th.closest("table.sortable");
    if (!table) return;
    var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
    var type = th.dataset.type === "num" ? "num" : "text";
    var dir = th.dataset.dir === "asc" ? "desc" : "asc";
    apply(table, idx, type, dir);
    // Remember the active sort on the swap container so HTMX filters keep it.
    var wrap = table.parentNode;
    if (wrap && wrap.dataset) wrap.dataset.sortState = idx + ":" + type + ":" + dir;
  });

  // Apply the remembered sort if there is one, else the table's declared default
  // (a th[data-sort-default="asc|desc"]). Records the choice so it survives swaps.
  function initTable(table) {
    var wrap = table.parentNode;
    if (wrap && wrap.dataset && wrap.dataset.sortState !== undefined) {
      var p = wrap.dataset.sortState.split(":");
      apply(table, parseInt(p[0], 10), p[1], p[2]);
      return;
    }
    var dth = table.querySelector("th[data-sort-default]");
    if (!dth) return;
    var idx = Array.prototype.indexOf.call(dth.parentNode.children, dth);
    var type = dth.dataset.type === "num" ? "num" : "text";
    var dir = dth.dataset.sortDefault === "asc" ? "asc" : "desc";
    apply(table, idx, type, dir);
    if (wrap && wrap.dataset) wrap.dataset.sortState = idx + ":" + type + ":" + dir;
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("table.sortable").forEach(initTable);
  });

  // After HTMX swaps a fresh table in, re-apply the remembered sort (or default).
  document.body.addEventListener("htmx:afterSwap", function (e) {
    var wrap = e.target;
    var table = wrap && wrap.querySelector ? wrap.querySelector("table.sortable") : null;
    if (table) initTable(table);
  });
})();
