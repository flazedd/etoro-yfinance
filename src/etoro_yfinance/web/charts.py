"""Server-rendered SVG charts for the web UI — no JS charting lib, works offline.

price_volume_svg() draws a split-adjusted price line over a volume panel from a
ticker's stored OHLCV (data/prices/<ticker>.parquet), bucket-downsampled so even
decades of daily bars render as a compact, readable inline SVG.
"""

from __future__ import annotations

import html
import json
import math
from typing import Any

_W, _H = 880, 400
_PAD_L, _PAD_R, _PAD_T, _PAD_B = 60, 14, 12, 26
_BUCKETS = 420  # target x-resolution; daily history is downsampled to this


def fmt_price(v: float) -> str:
    if v >= 1000:
        return f"{v:,.0f}"
    if v >= 1:
        return f"{v:,.2f}"
    return f"{v:.4f}"


def _fmt_vol(v: float) -> str:
    for unit, div in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if v >= div:
            return f"{v / div:.1f}{unit}"
    return f"{v:.0f}"


def _downsample(
    dates: list[Any], price: list[float], vol: list[float]
) -> tuple[list[Any], list[float], list[float]]:
    """Bucket into ~_BUCKETS points: last price in each bucket, max volume."""
    n = len(price)
    if n <= _BUCKETS:
        return list(dates), list(price), list(vol)
    step = math.ceil(n / _BUCKETS)
    ds, ps, vs = [], [], []
    for i in range(0, n, step):
        j = min(i + step, n)
        ds.append(dates[j - 1])
        ps.append(price[j - 1])
        vs.append(max(vol[i:j]))
    return ds, ps, vs


def price_volume_svg(df: Any, log: bool = True) -> str | None:
    """Build an inline SVG (price line + volume bars) from a stored OHLCV frame,
    or None if there's no usable price series. Uses adj_close (continuous through
    splits) for the price line; log scale on price by default."""
    field = "adj_close" if "adj_close" in df.columns else "close"
    rows = [
        (d, float(p), float(v))
        for d, p, v in zip(df.index, df[field], df["volume"], strict=False)
        if p == p
    ]  # drop NaN prices
    if len(rows) < 2:
        return None
    dates = [r[0] for r in rows]
    price = [r[1] for r in rows]
    vol = [r[2] for r in rows]
    dates, price, vol = _downsample(dates, price, vol)

    n = len(price)
    pmin, pmax = min(price), max(price)
    if pmax == pmin:
        pmax = pmin + 1
    vmax = max(vol) or 1
    # Log price needs a strictly positive domain; fall back to linear otherwise.
    use_log = log and pmin > 0

    plot_h = _H - _PAD_T - _PAD_B
    price_h = plot_h * 0.62  # price panel
    gap = plot_h * 0.06  # gap between panels
    vol_h = plot_h * 0.30  # taller volume panel
    vol_top = _PAD_T + price_h + gap
    vol_base = vol_top + vol_h  # the flat x-axis the bars stand on
    inner_w = _W - _PAD_L - _PAD_R

    def x(i: int) -> float:
        return _PAD_L + inner_w * (i / (n - 1))

    if use_log:
        lmin, lmax = math.log10(pmin), math.log10(pmax)
        span = (lmax - lmin) or 1.0

        def py(p: float) -> float:
            return _PAD_T + price_h * (1 - (math.log10(max(p, 1e-9)) - lmin) / span)
    else:

        def py(p: float) -> float:
            return _PAD_T + price_h * (1 - (p - pmin) / (pmax - pmin))

    line = " ".join(f"{x(i):.1f},{py(price[i]):.1f}" for i in range(n))

    # Volume bars stand on the flat baseline (vol_base); non-zero bars get a
    # visible minimum height so nothing disappears against the axis.
    bar_w = max(0.8, inner_w / n * 0.8)
    parts = []
    for i in range(n):
        h = vol_h * (vol[i] / vmax)
        if vol[i] > 0:
            h = max(h, 0.8)
        parts.append(
            f'<rect x="{x(i) - bar_w / 2:.1f}" y="{vol_base - h:.1f}" '
            f'width="{bar_w:.1f}" height="{h:.1f}" fill="#94a3b8"/>'
        )
    bars = "".join(parts)

    d0, d1 = str(dates[0]), str(dates[-1])
    e = html.escape
    return f"""<svg viewBox="0 0 {_W} {_H}" class="pv-chart" role="img"
     preserveAspectRatio="xMidYMid meet">
  <!-- price grid + labels -->
  <line x1="{_PAD_L}" y1="{_PAD_T:.1f}" x2="{_W - _PAD_R}" y2="{_PAD_T:.1f}" stroke="#e2e8f0"/>
  <line x1="{_PAD_L}" y1="{_PAD_T + price_h:.1f}" x2="{_W - _PAD_R}" y2="{_PAD_T + price_h:.1f}" stroke="#e2e8f0"/>
  <text x="{_PAD_L - 6}" y="{_PAD_T + 4:.1f}" text-anchor="end" class="pv-axis">{e(fmt_price(pmax))}</text>
  <text x="{_PAD_L - 6}" y="{_PAD_T + price_h:.1f}" text-anchor="end" class="pv-axis">{e(fmt_price(pmin))}</text>
  <polyline points="{line}" fill="none" stroke="#2563eb" stroke-width="1.4"/>
  <!-- volume: bars standing on a flat baseline -->
  {bars}
  <line x1="{_PAD_L}" y1="{vol_base:.1f}" x2="{_W - _PAD_R}" y2="{vol_base:.1f}" stroke="#cbd5e1"/>
  <text x="{_PAD_L - 6}" y="{vol_top + 4:.1f}" text-anchor="end" class="pv-axis">{e(_fmt_vol(vmax))}</text>
  <text x="{_PAD_L - 6}" y="{vol_base:.1f}" text-anchor="end" class="pv-axis">0</text>
  <!-- x dates -->
  <text x="{_PAD_L}" y="{_H - 8}" text-anchor="start" class="pv-axis">{e(d0)}</text>
  <text x="{_W - _PAD_R}" y="{_H - 8}" text-anchor="end" class="pv-axis">{e(d1)}</text>
</svg>"""


# Palette for equity-curve lines (strategy first, benchmark muted).
_LINE_COLORS = ["#2563eb", "#94a3b8", "#059669", "#d97706"]


def equity_svg(dates: list[str], series: dict[str, list[float]], log: bool = True) -> str:
    """Multi-line equity-curve SVG (log y by default) with a legend. Each series
    is an equity curve (starts at 1.0); `dates` is the shared x (ISO strings)."""
    vals = [v for s in series.values() for v in s if v is not None and v > 0]
    if len(vals) < 2:
        return '<svg viewBox="0 0 880 360" class="pv-chart"></svg>'
    lo, hi = min(vals), max(vals)
    if log:
        lo, hi = math.log10(lo), math.log10(hi)
    if hi == lo:
        hi = lo + 1
    n = max(len(dates), 2)
    ph = _H - _PAD_T - _PAD_B
    inner_w = _W - _PAD_L - _PAD_R

    def x(i: int) -> float:
        return _PAD_L + inner_w * (i / (n - 1))

    def y(v: float) -> float:
        t = math.log10(v) if log else v
        return _PAD_T + ph * (1 - (t - lo) / (hi - lo))

    e = html.escape
    lines, legend = [], []
    for k, (name, ys) in enumerate(series.items()):
        color = _LINE_COLORS[k % len(_LINE_COLORS)]
        pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(ys) if v and v > 0)
        lines.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.6"/>')
        ly = _PAD_T + 12 + k * 15
        legend.append(
            f'<rect x="{_PAD_L + 6}" y="{ly - 8}" width="10" height="10" fill="{color}"/>'
            f'<text x="{_PAD_L + 20}" y="{ly + 1}" class="pv-axis">{e(name)} '
            f"(×{ys[-1]:.2f})</text>"
        )
    # y grid labels (top/bottom of the value range)
    top_v = (10**hi) if log else hi
    bot_v = (10**lo) if log else lo
    # Data for the JS hover (base.html): dates + rounded series, single-quoted
    # attrs so the JSON double-quotes are valid (values have no single quotes).
    d_dates = json.dumps(dates)
    d_series = json.dumps({k: [round(v, 4) for v in ys] for k, ys in series.items()})
    return f"""<svg viewBox="0 0 {_W} {_H}" class="pv-chart eq-chart" role="img"
     preserveAspectRatio="xMidYMid meet" data-x0="{_PAD_L}" data-x1="{_W - _PAD_R}"
     data-dates='{d_dates}' data-series='{d_series}'>
  <line x1="{_PAD_L}" y1="{_PAD_T}" x2="{_W - _PAD_R}" y2="{_PAD_T}" stroke="#e2e8f0"/>
  <line x1="{_PAD_L}" y1="{_PAD_T + ph:.1f}" x2="{_W - _PAD_R}" y2="{_PAD_T + ph:.1f}" stroke="#e2e8f0"/>
  <text x="{_PAD_L - 6}" y="{_PAD_T + 4}" text-anchor="end" class="pv-axis">×{top_v:.2f}</text>
  <text x="{_PAD_L - 6}" y="{_PAD_T + ph:.1f}" text-anchor="end" class="pv-axis">×{bot_v:.2f}</text>
  {"".join(lines)}
  {"".join(legend)}
  <line class="eq-cross" x1="{_PAD_L}" x2="{_PAD_L}" y1="{_PAD_T}" y2="{_PAD_T + ph:.1f}"
        stroke="#64748b" stroke-dasharray="3 3" style="display:none"/>
  <text x="{_PAD_L}" y="{_H - 8}" text-anchor="start" class="pv-axis">{e(dates[0])}</text>
  <text x="{_W - _PAD_R}" y="{_H - 8}" text-anchor="end" class="pv-axis">{e(dates[-1])}</text>
</svg>"""
