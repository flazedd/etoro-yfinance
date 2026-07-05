"""FastAPI app — read-only views over the eToro→yfinance universe. No credentials.

The app reads a single offline-built artifact (data/etoro_universe_mapping.json)
and system diagnostics. It never calls eToro or any broker — trading lives in the
CLI (scripts/etoro_trade.py). Pages: Home, eToro↔yfinance universe, Diagnostics.
"""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from etoro_yfinance import universe as universe_mod
from etoro_yfinance.yfinance_map import is_crypto_quote_dupe, is_future

from . import data as datamod
from . import diagnostics as diag

_HERE = Path(__file__).parent
_UNIVERSE_CAP = 1500  # rows rendered at once (the universe is ~15.5k)


def create_app() -> FastAPI:
    app = FastAPI(title="eToro ↔ yfinance", docs_url=None, redoc_url=None)
    templates = Jinja2Templates(directory=str(_HERE / "templates"))
    app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")

    # Cache-bust static assets by the newest stylesheet mtime (tailwind + app).
    try:
        css = (_HERE / "static" / "tailwind.css", _HERE / "static" / "app.css")
        asset_v = str(int(max(p.stat().st_mtime for p in css)))
    except OSError:
        asset_v = "0"
    templates.env.globals["asset_v"] = asset_v

    def page(request: Request, name: str, ctx: dict[str, Any]) -> HTMLResponse:
        return templates.TemplateResponse(request, name, {"active": ctx.pop("active", ""), **ctx})

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return page(request, "home.html", {"active": "home", "home": _home_summary()})

    # ── eToro universe → yfinance mapping (read-only; built offline) ──────────
    @app.get("/universe", response_class=HTMLResponse)
    def universe(
        request: Request,
        q: str = "",
        asset_type: str = "",
        status: str = "",
        show_internal: bool = False,
        min_adv: str = "",
        sector: str = "",
        view: str = "",
    ) -> HTMLResponse:
        ctx = _universe_ctx(
            q=q,
            asset_type=asset_type,
            status=status,
            show_internal=show_internal,
            min_adv=min_adv,
            sector=sector,
            view=view,
        )
        age = datamod.snapshot_age_seconds("etoro_universe_mapping.json", time.time())
        return page(
            request,
            "universe.html",
            {
                "active": "universe",
                "age": age,
                "q": q,
                "show_internal": show_internal,
                "min_adv": min_adv,
                **ctx,
            },
        )

    @app.get("/universe/rows", response_class=HTMLResponse)
    def universe_rows(
        request: Request,
        q: str = "",
        asset_type: str = "",
        status: str = "",
        show_internal: bool = False,
        min_adv: str = "",
        sector: str = "",
        view: str = "",
    ) -> HTMLResponse:
        ctx = _universe_ctx(
            q=q,
            asset_type=asset_type,
            status=status,
            show_internal=show_internal,
            min_adv=min_adv,
            sector=sector,
            view=view,
        )
        return templates.TemplateResponse(request, "_universe_rows.html", {"oob": True, **ctx})

    @app.get("/universe/rules", response_class=HTMLResponse)
    def universe_rules(
        request: Request, t: str = "", name: str = "", sym: str = ""
    ) -> HTMLResponse:
        """Modal fragment: the full eToro trading rule set for one instrument id."""
        rules = datamod.load_instrument_rules(t) if t else None
        return templates.TemplateResponse(
            request, "_rules.html", {"rules": rules, "iid": t, "name": name, "sym": sym}
        )

    @app.get("/universe/new", response_class=HTMLResponse)
    def universe_new(request: Request) -> HTMLResponse:
        """The create-universe criteria form (modal)."""
        return templates.TemplateResponse(request, "_universe_new.html", {})

    @app.post("/universe/create", response_class=HTMLResponse)
    def universe_create(
        request: Request,
        name: Annotated[str, Form()] = "backtest",
        min_adv: Annotated[str, Form()] = "1000000",
        min_bars: Annotated[str, Form()] = "252",
        recent_days: Annotated[str, Form()] = "7",
        max_spread: Annotated[str, Form()] = "",
        require_sector: Annotated[str, Form()] = "",
    ) -> HTMLResponse:
        """Build + persist a universe under the criteria, return a confirmation
        (count, per-condition verification, per-sector breakdown). POST: it
        writes data/universe_<name>.json — must not be reachable by a prefetch."""
        doc = universe_mod.save(
            name,
            min_adv=_to_float(min_adv),
            min_bars=int(_to_float(min_bars)),
            recent_days=int(_to_float(recent_days)) or None,
            max_spread=(_to_float(max_spread) if max_spread.strip() else None),
            require_sector=(require_sector == "true"),
        )
        return templates.TemplateResponse(request, "_universe_created.html", {"doc": doc})

    @app.get("/universe/chart", response_class=HTMLResponse)
    def universe_chart(
        request: Request, t: str = "", name: str = "", scale: str = "log"
    ) -> HTMLResponse:
        """Modal fragment: side-by-side price+volume charts for one yfinance
        ticker — native (left) and EUR-converted (right), read from the local
        Parquet stores. Log price by default (scale=linear switches both)."""
        from etoro_yfinance import currency, prices

        from . import charts

        log = scale != "linear"

        def panel(
            df: Any,
        ) -> tuple[str | None, tuple[str, str, int] | None, str | None, str | None]:
            if df is None or len(df) == 0:
                return None, None, None, None
            svg = charts.price_volume_svg(df, log=log)
            span = (str(df.index[0]), str(df.index[-1]), len(df))
            close = (df["close"] if "close" in df.columns else df["adj_close"]).dropna()
            last = (
                (charts.fmt_price(float(close.iloc[-1])), str(close.index[-1]))
                if len(close)
                else (None, None)
            )
            return svg, span, last[0], last[1]

        native = panel(prices.load_prices(t) if t else None)
        eur = panel(prices.load_prices(t, eur=True) if t else None)
        ccy = currency.currency_for(t, None) if t else None
        return templates.TemplateResponse(
            request,
            "_chart.html",
            {
                "ticker": t,
                "name": name,
                "log": log,
                "ccy": ccy or "native",
                "svg": native[0],
                "span": native[1],
                "last_price": native[2],
                "last_date": native[3],
                "svg_eur": eur[0],
                "last_eur": eur[2],
                "last_date_eur": eur[3],
            },
        )

    # ── backtest (monthly momentum on a chosen universe) ─────────────────────
    @app.get("/backtest", response_class=HTMLResponse)
    def backtest_page(request: Request) -> HTMLResponse:
        from etoro_yfinance import backtest as bt
        from etoro_yfinance import momentum

        rows = datamod.load_etoro_universe().get("rows", [])
        latest = max((r.get("price_to") or "" for r in rows), default="")
        by_id = {r.get("instrument_id"): r for r in rows}

        def _member_rows(doc: dict[str, Any]) -> list[dict[str, Any]]:
            # Prefer the live snapshot row (it carries vol_from); fall back to
            # the saved instrument (older docs persisted price_from only).
            members = []
            for inst in doc.get("instruments", []):
                r = by_id.get(inst.get("instrument_id"))
                members.append(r if r and r.get("price_from") else inst)
            return members

        def _sector_counts(members: list[dict[str, Any]]) -> list[dict[str, Any]]:
            c = Counter((r.get("sector") or "(none)") for r in members)
            return [
                {"name": k, "count": v}
                for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
            ]

        # Per saved universe: name, instrument count, the earliest start where
        # every member already has 2y of price+volume history, and the sector
        # mix (drives the sector checkboxes on the form).
        saved = []
        sectors_by_view: dict[str, list[dict[str, Any]]] = {}
        for u in universe_mod.list_saved():
            doc = universe_mod.load(u)
            members = _member_rows(doc)
            sectors_by_view[u] = _sector_counts(members)
            saved.append(
                {
                    "name": u,
                    "count": doc.get("count"),
                    "start": universe_mod.earliest_start(members),
                }
            )
        default_rows = universe_mod.select(rows=rows)
        sectors_by_view[""] = _sector_counts(default_rows)
        default_start = universe_mod.earliest_start(default_rows)
        default_view = "backtest" if any(s["name"] == "backtest" for s in saved) else ""
        selected_start = next((s["start"] for s in saved if s["name"] == default_view), None)
        return page(
            request,
            "backtest.html",
            {
                "active": "backtest",
                "saved_universes": saved,
                "sectors_by_view": sectors_by_view,
                "default_view": default_view,
                "default_start": default_start,
                "strategies": bt.STRATEGIES,
                "rebalances": list(bt.REBALANCE),
                "strategy": momentum.strategy_signals(),
                "end_default": latest or str(date.today()),
                "start_default": selected_start or default_start or "2018-01-01",
            },
        )

    @app.get("/backtest/run", response_class=HTMLResponse)
    def backtest_run(
        request: Request,
        view: str = "",
        start: str = "2018-01-01",
        end: str = "",
        strategy: str = "momentum",
        rebalance: str = "monthly",
        top_n_sectors: str = "4",
        top_n_per_sector: str = "6",
        min_sector_size: str = "0",
        min_price_score: str = "30",
        top_n: str = "30",
        window: str = "develop",
        trend_filter: str = "",
        vol_target: str = "0",
        sectors: Annotated[list[str] | None, Query()] = None,
        sectors_filter: str = "",
    ) -> HTMLResponse:
        """Kick off the backtest in a background thread; return a polling progress
        bar. Results are fetched by /backtest/progress once done."""
        from etoro_yfinance import backtest as bt

        # Develop/validate split: strategies are tuned on the develop window
        # only; "validate" is the single switch for the held-out test. Custom
        # uses the submitted dates.
        if window == "develop":
            start, end = "2005-01-01", "2019-01-01"
        elif window == "validate":
            start, end = "2019-01-01", str(date.today())
        elif window == "full":
            start, end = "2005-01-01", str(date.today())

        rows = (
            universe_mod.load(view).get("instruments", [])
            if view in universe_mod.list_saved()
            else universe_mod.select()
        )
        view_label = view or "(default)"
        # Sector checkboxes on the form (sectors_filter marks that they were
        # rendered — absent means an old/JS-less form, i.e. no filtering).
        if sectors_filter:
            allowed = set(sectors or [])
            if not allowed:
                return templates.TemplateResponse(
                    request,
                    "_backtest_result.html",
                    {
                        "res": {"error": "no sectors selected — tick at least one"},
                        "chart": None,
                        "view": view_label,
                    },
                )
            all_sectors = {(r.get("sector") or "(none)") for r in rows}
            if not all_sectors <= allowed:
                rows = [r for r in rows if (r.get("sector") or "(none)") in allowed]
                view_label = f"{view_label} · {len(allowed & all_sectors)}/{len(all_sectors)} sectors"
        _reap_jobs(time.time())
        job_id = uuid.uuid4().hex[:12]
        with _BT_LOCK:
            _BT_JOBS[job_id] = {
                "pct": 0.0,
                "label": "starting…",
                "result": None,
                "error": None,
                "view": view_label,
                "ts": time.time(),
            }

        def _update(**fields: Any) -> None:
            """Touch the job if it still exists (it may have been reaped)."""
            with _BT_LOCK:
                if job_id in _BT_JOBS:
                    _BT_JOBS[job_id].update(ts=time.time(), **fields)

        def _progress(frac: float, label: str) -> None:
            _update(pct=frac, label=label)

        def _worker() -> None:
            try:
                res = bt.run(
                    rows,
                    start=start,
                    end=end or str(date.today()),
                    strategy=strategy or "momentum",
                    rebalance=rebalance or "monthly",
                    top_n_sectors=int(_to_float(top_n_sectors)) or 4,
                    top_n_per_sector=int(_to_float(top_n_per_sector)) or 6,
                    min_sector_size=int(_to_float(min_sector_size)),
                    min_price_score=_to_float(min_price_score),
                    top_n=int(_to_float(top_n)) or 30,
                    trend_filter=bool(trend_filter),
                    vol_target=_to_float(vol_target),
                    progress=_progress,
                )
                _update(pct=1.0, result=res)
            except Exception as e:  # surface failures to the poller
                _update(pct=1.0, error=str(e))

        threading.Thread(target=_worker, daemon=True).start()
        return templates.TemplateResponse(
            request, "_backtest_running.html", {"job_id": job_id, "pct": 0, "label": "starting…"}
        )

    @app.get("/backtest/progress", response_class=HTMLResponse)
    def backtest_progress(request: Request, job: str = "") -> HTMLResponse:
        _reap_jobs(time.time())
        with _BT_LOCK:
            j = dict(_BT_JOBS.get(job) or {})
        if not j:
            return templates.TemplateResponse(
                request,
                "_backtest_result.html",
                {"res": {"error": "job expired — re-run"}, "chart": None, "view": ""},
            )
        if j.get("result") is None and not j.get("error"):
            return templates.TemplateResponse(
                request,
                "_backtest_running.html",
                {"job_id": job, "pct": j["pct"], "label": j["label"]},
            )
        # Done (or failed): render results and drop the job.
        with _BT_LOCK:
            _BT_JOBS.pop(job, None)
        res = j.get("result") or {"error": j.get("error")}
        # Equity curves for the client-side chart (Lightweight Charts in
        # _backtest_result.html), indexed to 100 at the start; round() also
        # converts numpy floats to JSON-able ones.
        chart = (
            {
                "dates": res["dates"],
                "series": [
                    {"name": "Strategy", "values": [round(v * 100, 2) for v in res["equity"]]},
                    {
                        "name": "Benchmark",
                        "values": [round(v * 100, 2) for v in res["benchmark"]],
                    },
                ],
            }
            if "error" not in res
            else None
        )
        return templates.TemplateResponse(
            request,
            "_backtest_result.html",
            {"res": res, "chart": chart, "view": j.get("view", "")},
        )

    # ── alpha lab (signal IC scoreboard) ─────────────────────────────────────
    @app.get("/alphalab", response_class=HTMLResponse)
    def alphalab_page(request: Request) -> HTMLResponse:
        from etoro_yfinance import signals as sig

        saved = [
            {"name": u, "count": universe_mod.load(u).get("count")}
            for u in universe_mod.list_saved()
        ]
        return page(
            request,
            "alphalab.html",
            {
                "active": "alphalab",
                "saved_universes": saved,
                "default_view": "backtest" if any(s["name"] == "backtest" for s in saved) else "",
                "signals": [
                    {
                        "name": s.name,
                        "family": s.family,
                        "sign": s.sign,
                        "description": s.description,
                        "explanation": s.explanation,
                    }
                    for s in sig.SIGNALS
                ],
                "n_families": len({s.family for s in sig.SIGNALS}),
            },
        )

    @app.get("/alphalab/run", response_class=HTMLResponse)
    def alphalab_run(
        request: Request, view: str = "backtest", window: str = "develop", fdr_q: str = "0.10"
    ) -> HTMLResponse:
        """Score all registered signals in a background thread (same job store
        + polling pattern as the backtest). Admission = the four-gate battery
        in signals.evaluate (FDR-corrected bootstrap confidence, long-only
        tradability net of spreads, yearly/asset-class robustness, decile
        monotonicity)."""
        from etoro_yfinance import signals as sig

        if window == "validate":
            start, end = "2019-01-01", str(date.today())
        elif window == "full":
            start, end = "2005-01-01", str(date.today())
        else:
            window = "develop"
            start, end = "2005-01-01", "2019-01-01"
        rows = (
            universe_mod.load(view).get("instruments", [])
            if view in universe_mod.list_saved()
            else universe_mod.select()
        )
        q = _to_float(fdr_q) or 0.10
        _reap_jobs(time.time())
        job_id = uuid.uuid4().hex[:12]
        with _BT_LOCK:
            _BT_JOBS[job_id] = {
                "pct": 0.0,
                "label": "starting…",
                "result": None,
                "error": None,
                "view": f"{view or '(default)'} · {window}",
                "ts": time.time(),
            }

        def _update(**fields: Any) -> None:
            with _BT_LOCK:
                if job_id in _BT_JOBS:
                    _BT_JOBS[job_id].update(ts=time.time(), **fields)

        def _worker() -> None:
            import warnings

            try:
                with warnings.catch_warnings():
                    # all-NaN windows are routine for young/stale names
                    warnings.simplefilter("ignore", RuntimeWarning)
                    ctx = sig.build_context(
                        rows, start, end, progress=lambda f, s: _update(pct=0.5 * f, label=s)
                    )
                    board, detail = sig.evaluate(
                        ctx,
                        start,
                        end,
                        fdr_q=q,
                        with_detail=True,
                        progress=lambda f, s: _update(pct=0.5 + 0.3 * f, label=s),
                    )
                    # admitted signals first, then by |t| within each group
                    board = board.sort_values(
                        ["admitted", "t_stat"],
                        ascending=False,
                        key=lambda c: c.abs() if c.name == "t_stat" else c.fillna(False),
                    )
                    admitted = board[board["admitted"].fillna(False)]["signal"].tolist()
                    _update(pct=0.82, label="combining")
                    combo_all = sig.combo_ic(ctx, start, end)
                    combo_adm = sig.combo_ic(ctx, start, end, admitted) if admitted else None
                    red = sig.redundancy(
                        ctx, start, end, progress=lambda f, s: _update(pct=0.85 + 0.15 * f, label=s)
                    )
                pairs = red.stack().sort_values(key=abs, ascending=False)
                regimes = sig.regime_series(ctx, start, end)
                result = {
                    "run_id": job_id,
                    "window": window,
                    "start": start,
                    "end": end,
                    "fdr_q": q,
                    "universe": view or "(default)",
                    "names": len(ctx.names),
                    "regimes": regimes,
                    "board": board.where(board.notna(), None).to_dict("records"),
                    "admitted": admitted,
                    "combo_all": combo_all,
                    "combo_admitted": combo_adm,
                    "pairs": [
                        {"a": a, "b": b, "corr": round(float(v), 2)}
                        for (a, b), v in pairs.items()
                        if abs(v) >= 0.6
                    ],
                }
                # Persist the run (board + per-signal series): the library's
                # history stays auditable, and the per-signal chart modal reads
                # its data from here after the in-memory job is dropped.
                out_dir = datamod.data_dir() / "alphalab"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / f"{job_id}.json").write_text(
                    json.dumps({**result, "created": time.time(), "detail": detail})
                )
                _update(pct=1.0, result=result)
            except Exception as e:  # surface failures to the poller
                _update(pct=1.0, error=str(e))

        threading.Thread(target=_worker, daemon=True).start()
        return templates.TemplateResponse(
            request, "_alphalab_running.html", {"job_id": job_id, "pct": 0, "label": "starting…"}
        )

    @app.get("/alphalab/progress", response_class=HTMLResponse)
    def alphalab_progress(request: Request, job: str = "") -> HTMLResponse:
        from etoro_yfinance import signals as sig

        explain = {s.name: s.explanation for s in sig.SIGNALS}
        flag_info = sig.FLAG_INFO
        _reap_jobs(time.time())
        with _BT_LOCK:
            j = dict(_BT_JOBS.get(job) or {})
        if not j:
            return templates.TemplateResponse(
                request,
                "_alphalab_result.html",
                {"res": {"error": "job expired — re-run"}, "view": "", "explain": explain, "flag_info": flag_info},
            )
        if j.get("result") is None and not j.get("error"):
            return templates.TemplateResponse(
                request,
                "_alphalab_running.html",
                {"job_id": job, "pct": j["pct"], "label": j["label"]},
            )
        with _BT_LOCK:
            _BT_JOBS.pop(job, None)
        res = j.get("result") or {"error": j.get("error")}
        return templates.TemplateResponse(
            request,
            "_alphalab_result.html",
            {"res": res, "view": j.get("view", ""), "explain": explain, "flag_info": flag_info},
        )

    @app.get("/alphalab/cached", response_class=HTMLResponse)
    def alphalab_cached(
        request: Request, view: str = "backtest", window: str = "develop", fdr_q: str = "0.10"
    ) -> HTMLResponse:
        """The newest persisted run matching (universe, window, fdr_q, signal
        set), rendered instantly — Score signals stays the explicit re-run."""
        from etoro_yfinance import signals as sig

        q = _to_float(fdr_q) or 0.10
        window = window if window in ("validate", "full") else "develop"
        wanted_universe = view or "(default)"
        current_signals = sorted(s.name for s in sig.SIGNALS)
        best: dict[str, Any] | None = None
        run_dir = datamod.data_dir() / "alphalab"
        if run_dir.exists():
            for p in run_dir.glob("*.json"):
                try:
                    doc = json.loads(p.read_text())
                except (OSError, ValueError):
                    continue
                if (
                    doc.get("universe") != wanted_universe
                    or doc.get("window") != window
                    or abs(float(doc.get("fdr_q", -1)) - q) > 1e-9
                    or sorted(r.get("signal", "") for r in doc.get("board", [])) != current_signals
                ):
                    continue
                if best is None or doc.get("created", 0) > best.get("created", 0):
                    best = doc
        if best is None:
            return HTMLResponse(
                '<div class="text-sm text-slate-500">no cached run for these settings — '
                "hit <b>Score signals</b> to compute one (results are cached from then on).</div>"
            )
        created = float(best.get("created", 0))
        best["cached_at"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(created))
        # data-moved hint: the universe/price snapshot is newer than this run
        snap_age = datamod.snapshot_age_seconds("etoro_universe_mapping.json", time.time())
        best["data_moved"] = snap_age is not None and (time.time() - created) > snap_age
        best.pop("detail", None)  # charts read the file; no need to render it
        return templates.TemplateResponse(
            request,
            "_alphalab_result.html",
            {
                "res": best,
                "view": f"{best['universe']} · {window}",
                "explain": {s.name: s.explanation for s in sig.SIGNALS},
                "flag_info": sig.FLAG_INFO,
            },
        )

    @app.get("/alphalab/chart", response_class=HTMLResponse)
    def alphalab_chart(request: Request, run: str = "", signal: str = "") -> HTMLResponse:
        """Per-signal evidence modal: charts + the full metric grid, read from
        the persisted run file (mirrors the per-instrument price/volume modal)."""
        from etoro_yfinance import signals as sig

        err = None
        doc = row = series = s_def = None
        if not run.isalnum():
            err = "bad run id"
        else:
            path = datamod.data_dir() / "alphalab" / f"{run}.json"
            if not path.exists():
                err = "run not found — re-run the scoreboard (results persist from now on)"
            else:
                doc = json.loads(path.read_text())
                row = next((r for r in doc.get("board", []) if r.get("signal") == signal), None)
                series = doc.get("detail", {}).get("signals", {}).get(signal)
                s_def = next((s for s in sig.SIGNALS if s.name == signal), None)
                if row is None or series is None:
                    err = f"no data for signal {signal!r} in this run"
        return templates.TemplateResponse(
            request,
            "_alphalab_chart.html",
            {
                "error": err,
                "signal": signal,
                "row": row,
                "series": series,
                "meta": doc or {},
                "explanation": s_def.explanation if s_def else "",
                "description": s_def.description if s_def else "",
                "flag_info": sig.FLAG_INFO,
            },
        )

    # ── diagnostics (system health) ──────────────────────────────────────────
    @app.get("/diagnostics", response_class=HTMLResponse)
    def diagnostics(request: Request) -> HTMLResponse:
        return page(request, "diagnostics.html", {"active": "diagnostics", "d": _diag()})

    @app.get("/api/diagnostics")
    def api_diagnostics() -> JSONResponse:
        return JSONResponse(_diag())

    @app.get("/healthz")
    def healthz() -> dict[str, bool]:
        return {"ok": True}

    return app


def _home_summary() -> dict[str, Any]:
    """Light rollup for the landing page — universe coverage + system health."""
    from etoro_yfinance import backtest as bt
    from etoro_yfinance import signals as sig

    snap = datamod.load_etoro_universe()
    return {
        "universe": {
            "counts": snap.get("counts", {}),
            "generated_at": snap.get("generated_at"),
            "age": datamod.snapshot_age_seconds("etoro_universe_mapping.json", time.time()),
        },
        "diagnostics": {"overall": _diag().get("overall")},
        "backtest": {
            "strategies": len(bt.STRATEGIES),
            "universes": len(universe_mod.list_saved()),
            "criteria": len(bt.STABILITY_CRITERIA),
        },
        "alphalab": {
            "signals": len(sig.SIGNALS),
            "families": len({s.family for s in sig.SIGNALS}),
        },
    }


def _diag() -> dict[str, Any]:
    now = time.time()
    return diag.collect(
        now,
        snapshots={
            "etoro universe": datamod.snapshot_age_seconds("etoro_universe_mapping.json", now),
        },
    )


# In-memory backtest jobs (single-process): id -> {pct, label, result, error,
# view, ts}. Results are dropped once fetched; _reap_jobs handles the browser
# that kicked off a run and never polled it, so the dict can't grow unbounded.
_BT_JOBS: dict[str, dict[str, Any]] = {}
_BT_LOCK = threading.Lock()
_BT_TTL = 3600.0  # seconds a job may sit untouched before it's reaped


def _reap_jobs(now: float) -> None:
    with _BT_LOCK:
        stale = [jid for jid, j in _BT_JOBS.items() if now - j.get("ts", now) > _BT_TTL]
        for jid in stale:
            del _BT_JOBS[jid]


def _universe_ctx(
    *,
    q: str,
    asset_type: str,
    status: str,
    show_internal: bool,
    min_adv: str,
    sector: str,
    view: str,
) -> dict[str, Any]:
    """The shared template context for the universe page and its HTMX row
    refresh: filtered rows (capped), facet counts, and column-visibility flags."""
    snap = datamod.load_etoro_universe()
    all_rows = snap.get("rows", [])
    saved = universe_mod.list_saved()
    madv = _to_float(min_adv)
    ids = universe_mod.member_ids(view) if view in saved else None
    rows = _filter_universe(
        all_rows,
        q=q,
        asset_type=asset_type,
        status=status,
        show_internal=show_internal,
        min_adv=madv,
        sector=sector,
        universe_ids=ids,
    )
    facets = _facet_counts(
        all_rows,
        q=q,
        asset_type=asset_type,
        status=status,
        sector=sector,
        min_adv=madv,
        show_internal=show_internal,
        view=view,
        saved=saved,
    )
    counts = snap.get("counts", {})
    return {
        "snap": snap,
        "rows": rows[:_UNIVERSE_CAP],
        "shown": len(rows),
        "asset_type": asset_type,
        "status": status,
        "sector": sector,
        "view": view,
        "saved_universes": saved,
        **facets,
        "validated": bool(counts.get("validated")),
        "eligible": bool(counts.get("eligibility_checked")),
        "liquid": bool(counts.get("liquidity_checked")),
        "has_sector": bool(counts.get("sector_known")),
    }


def _to_float(s: str) -> float:
    """Parse a query value to float; blank/invalid → 0.0 (empty form fields send '')."""
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def _filter_universe(
    rows: list[dict[str, Any]],
    *,
    q: str,
    asset_type: str,
    status: str,
    show_internal: bool = False,
    min_adv: float = 0.0,
    sector: str = "",
    universe_ids: set[Any] | None = None,
) -> list[dict[str, Any]]:
    ql = q.lower().strip()
    crypto_syms = {(r.get("symbol") or "").upper() for r in rows if r.get("status") == "crypto"}
    out = []
    for r in rows:
        # Restrict to a saved universe's members (by execution instrument_id).
        if universe_ids is not None and r.get("instrument_id") not in universe_ids:
            continue
        # Dated futures and non-USD-quoted crypto duplicates (BTCEUR vs BTC) are
        # never part of the spot universe — excluded here too so a pre-filter
        # snapshot can't leak them into the view.
        if is_future(r.get("symbol"), r.get("exchange")):
            continue
        if r.get("status") == "crypto" and is_crypto_quote_dupe(r.get("symbol"), crypto_syms):
            continue
        # Liquidity floor: drop names below the requested median €/day turnover
        # (rows with unknown turnover are dropped when a floor is set).
        if min_adv > 0 and (r.get("adv_eur") or 0) < min_adv:
            continue
        # Hide eToro synthetic/dormant instruments by default, unless the user
        # opted in or is explicitly filtering to status=internal.
        if not show_internal and status != "internal" and r.get("status") == "internal":
            continue
        if asset_type and r.get("type") != asset_type:
            continue
        if status and r.get("status") != status:
            continue
        if sector and (r.get("sector") or "") != sector:
            continue
        if ql and ql not in (
            f"{r.get('symbol', '')} {r.get('name', '')} {r.get('yf', '')}".lower()
        ):
            continue
        out.append(r)
    return out


def _facet_counts(
    rows: list[dict[str, Any]],
    *,
    q: str,
    asset_type: str,
    status: str,
    sector: str,
    min_adv: float,
    show_internal: bool,
    view: str,
    saved: list[str],
) -> dict[str, Any]:
    """Faceted option counts: each dropdown counts with every OTHER active filter
    applied (excluding its own selection), so the numbers show what picking each
    option would yield given the rest of the filters."""
    view_ids = universe_mod.member_ids(view) if view in saved else None

    def f(
        *,
        atype: str = asset_type,
        st: str = status,
        sc: str = sector,
        uids: set[Any] | None = view_ids,
    ) -> list[dict[str, Any]]:
        return _filter_universe(
            rows,
            q=q,
            asset_type=atype,
            status=st,
            sector=sc,
            min_adv=min_adv,
            show_internal=show_internal,
            universe_ids=uids,
        )

    types = Counter(
        r.get("type") for r in f(atype="") if r.get("status") != "internal"
    ).most_common()
    statuses = Counter(r.get("status") for r in f(st="")).most_common()
    sectors = Counter(
        r.get("sector") for r in f(sc="") if r.get("sector") and r.get("status") != "internal"
    ).most_common()
    no_view = f(uids=None)  # view facet ignores the view restriction
    mem = {u: universe_mod.member_ids(u) for u in saved}
    view_counts = [(u, sum(1 for r in no_view if r.get("instrument_id") in mem[u])) for u in saved]
    return {
        "types": types,
        "statuses": statuses,
        "sectors": sectors,
        "all_count": len(no_view),
        "view_counts": view_counts,
    }


app = create_app()


def main() -> int:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="eToro↔yfinance read-only web UI")
    parser.add_argument("--host", default=os.environ.get("MOMENTUM_WEB_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("MOMENTUM_WEB_PORT", "8800"))
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=os.environ.get("MOMENTUM_WEB_RELOAD", "").lower() in ("1", "true", "yes"),
        help="auto-restart on code changes (local dev only)",
    )
    args = parser.parse_args()

    reload_dirs = [str(_HERE.parent)] if args.reload else None
    uvicorn.run(
        "etoro_yfinance.web.server:app",
        host=args.host,
        port=args.port,
        log_level="info",
        reload=args.reload,
        reload_dirs=reload_dirs,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
