"""Render the rebalancer's run history into a self-contained HTML page.

Pure read side: this module only reads the run-record JSONs (written by
`run_record.RunRecorder`) and the rotating log file. It never touches a broker.
Shared by two front-ends:

  * scripts/build_dashboard.py — writes a static dashboard.html (no server).
  * dashboard_server.py        — serves the same page live + a /api/logs tail.

The page is vanilla JS with the data embedded as JSON, so the static file works
offline and the live server just re-renders with fresh data on each request.
"""

from __future__ import annotations

import json
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def load_records(report_dir: Path | None) -> list[dict[str, Any]]:
    """All run records, newest first. Tolerates malformed/partial files."""
    if report_dir is None or not report_dir.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in report_dir.glob("*.json"):
        try:
            rec = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(rec, dict):
            rec.setdefault("id", path.stem)
            records.append(rec)
    records.sort(key=lambda r: str(r.get("started_at") or r.get("id") or ""), reverse=True)
    return records


def tail_log(log_path: Path | None, n: int = 300) -> list[str]:
    """Last `n` lines of the log file (memory-bounded via deque)."""
    if log_path is None or not log_path.exists():
        return []
    try:
        with log_path.open("r", errors="replace") as fh:
            return list(deque(fh, maxlen=max(1, n)))
    except OSError:
        return []


def render_html(
    records: list[dict[str, Any]],
    *,
    log_tail: list[str] | None = None,
    live: bool = False,
    generated_at: datetime | None = None,
) -> str:
    payload = {
        "records": records,
        "logTail": log_tail or [],
        "live": live,
        "generatedAt": (generated_at or datetime.now(UTC)).isoformat(),
    }
    return _HTML.replace("/*__DATA__*/", json.dumps(payload, default=str))


_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>ibkr-rebalance dashboard</title>
<style>
 :root{--g:#137333;--y:#b06000;--r:#c5221f;--bg:#f6f7f9;--line:#e3e6ea;--ink:#1f2328}
 *{box-sizing:border-box} body{font:13px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:var(--bg);color:var(--ink)}
 header{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);padding:10px 16px;z-index:5;display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
 h1{font-size:15px;margin:0} .meta{color:#888;font-size:11px}
 .wrap{display:grid;grid-template-columns:minmax(380px,1fr) minmax(420px,1.2fr);gap:14px;padding:14px}
 @media(max-width:900px){.wrap{grid-template-columns:1fr}}
 .card{background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden}
 .card h2{font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:#666;margin:0;padding:8px 12px;border-bottom:1px solid var(--line);background:#fafbfc}
 table{border-collapse:collapse;width:100%} th,td{padding:6px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}
 th{font-size:11px;color:#777;background:#fafbfc} tbody tr{cursor:pointer} tbody tr:hover{background:#f3f6ff} tr.sel{background:#e8f0fe}
 .pill{padding:1px 8px;border-radius:9px;font-size:11px;font-weight:600;color:#fff;display:inline-block}
 .running{background:#1a56db} .success{background:var(--g)} .dry_run{background:#6b7280}
 .partial{background:var(--y)} .failed,.error,.aborted{background:var(--r)}
 .num{text-align:right;font-variant-numeric:tabular-nums} .mono{font-family:ui-monospace,Menlo,monospace;font-size:11px}
 .detail{padding:12px} .kv{display:grid;grid-template-columns:130px 1fr;gap:2px 10px;margin-bottom:10px}
 .kv div:nth-child(odd){color:#888} .sub{color:#888;font-size:11px}
 .bad{color:var(--r);font-weight:600} .ok{color:var(--g)}
 .mini{width:100%;font-size:12px} .mini td,.mini th{padding:3px 8px}
 pre{margin:0;padding:10px 12px;background:#0d1117;color:#d1d5db;font:11px/1.5 ui-monospace,Menlo,monospace;overflow:auto;max-height:60vh;white-space:pre-wrap;word-break:break-word}
 .empty{padding:18px;color:#999}
 .dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px}
 .live-on{background:var(--g)} .live-off{background:#bbb}
</style></head><body>
<header>
 <h1>ibkr-rebalance dashboard</h1>
 <span class="meta"><span id="livedot" class="dot"></span><span id="livetxt"></span> · <span id="gen"></span></span>
</header>
<div class="wrap">
 <div class="card"><h2>Runs</h2><div id="runs"></div></div>
 <div>
  <div class="card" style="margin-bottom:14px"><h2>Run detail</h2><div id="detail" class="detail"><div class="empty">Select a run.</div></div></div>
  <div class="card"><h2>Log tail</h2><pre id="log"></pre></div>
 </div>
</div>
<script>
const DATA = /*__DATA__*/;
let records = DATA.records, sel = null;
const esc=s=>(s==null?'':String(s)).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const fmtNum=v=>{const n=Number(v); return isFinite(n)?n.toLocaleString(undefined,{maximumFractionDigits:2}):(v==null?'':esc(v));};
const when=s=>{if(!s)return ''; const d=new Date(s); return isNaN(d)?esc(s):d.toLocaleString();};
const pill=s=>`<span class="pill ${esc(s)}">${esc(s)}</span>`;
function costPct(r){const c=r.report&&r.report.total_cost_pct_of_nav; return c==null?'':Number(c).toFixed(3)+'%';}
function nTrades(r){return (r.planned_trades||[]).length;}

function runsTable(){
 if(!records.length){document.getElementById('runs').innerHTML='<div class="empty">No runs recorded yet.</div>';return;}
 const rows=records.map(r=>`<tr data-id="${esc(r.id)}" class="${sel===r.id?'sel':''}">
   <td>${pill(r.status)}</td><td>${when(r.started_at)}</td>
   <td class="num">${r.nav?fmtNum(r.nav):''}</td>
   <td class="num">${nTrades(r)}</td><td class="num">${costPct(r)}</td>
   <td>${r.dry_run?'<span class="sub">dry</span>':''}</td></tr>`).join('');
 document.getElementById('runs').innerHTML=
   `<table><thead><tr><th>status</th><th>started</th><th class="num">NAV</th><th class="num">trades</th><th class="num">cost</th><th></th></tr></thead><tbody>${rows}</tbody></table>`;
 document.querySelectorAll('#runs tbody tr').forEach(tr=>tr.onclick=()=>{sel=tr.dataset.id;runsTable();detail();});
}

function detail(){
 const r=records.find(x=>x.id===sel); const el=document.getElementById('detail');
 if(!r){el.innerHTML='<div class="empty">Select a run.</div>';return;}
 const h=r.health||{}; const rep=r.report||{};
 let html=`<div class="kv">
  <div>status</div><div>${pill(r.status)} ${r.dry_run?'<span class="sub">(dry run)</span>':''}</div>
  <div>started</div><div>${when(r.started_at)}</div>
  <div>finished</div><div>${when(r.finished_at)||'<span class="sub">—</span>'}</div>
  <div>strategy</div><div>#${esc(r.strategy_id)} · as_of ${esc(r.as_of_date)}</div>
  <div>bbterminal</div><div>${h.is_healthy_strict?'<span class="ok">healthy_strict</span>':'<span class="bad">NOT healthy_strict</span>'} ${h.problems?('· '+esc(JSON.stringify(h.problems))):''}</div>
  <div>NAV (${esc(r.sizing_currency)})</div><div>${r.nav?fmtNum(r.nav):'<span class="sub">—</span>'}</div>`;
 if(r.abort_reason) html+=`<div>abort</div><div class="bad">${esc(r.abort_reason)}</div>`;
 if(r.error) html+=`<div>error</div><div class="bad">${esc(r.error)}</div>`;
 html+=`</div>`;

 const trades=rep.trades||r.planned_trades||[];
 if(trades.length){
  const hasFills = !!rep.trades;
  html+=`<table class="mini"><thead><tr><th>side</th><th class="num">qty</th><th>symbol</th>${hasFills?'<th class="num">fill</th><th class="num">slip%</th><th>status</th>':'<th>reason</th>'}</tr></thead><tbody>`+
   trades.map(t=>`<tr><td>${esc(t.side)}</td><td class="num">${esc(t.quantity)}</td><td>${esc(t.symbol)}</td>`+
     (hasFills
       ? `<td class="num">${t.fill_price?fmtNum(t.fill_price):''}</td><td class="num ${t.slippage_pct&&Number(t.slippage_pct)>0?'bad':''}">${t.slippage_pct?Number(t.slippage_pct).toFixed(2):''}</td><td class="${t.success?'ok':'bad'}">${esc(t.final_status||(t.success?'ok':'fail'))}${t.error?(' — '+esc(t.error)):''}</td>`
       : `<td class="sub">${esc(t.reason)}</td>`)+`</tr>`).join('')+`</tbody></table>`;
  if(hasFills) html+=`<div class="sub" style="padding:6px 2px">filled ${esc(rep.n_successful)}/${esc(rep.n_total)} · total cost ${costPct(r)} of NAV</div>`;
 } else {
  html+=`<div class="sub" style="padding:6px 2px">no trades ${r.status==='running'?'computed yet':'needed'}</div>`;
 }
 el.innerHTML=html;
}

function renderLog(lines){document.getElementById('log').textContent=(lines&&lines.length)?lines.join(''):'(no log output)';}
function meta(){
 document.getElementById('gen').textContent='generated '+when(DATA.generatedAt);
 const on=DATA.live; document.getElementById('livedot').className='dot '+(on?'live-on':'live-off');
 document.getElementById('livetxt').textContent=on?'live':'static snapshot';
}
async function poll(){
 try{
  const rr=await fetch('api/runs',{cache:'no-store'}); if(rr.ok){records=await rr.json(); runsTable(); detail();}
  const lr=await fetch('api/logs',{cache:'no-store'}); if(lr.ok){renderLog((await lr.json()).lines);}
 }catch(e){/* server gone / offline — keep last view */}
}
meta(); runsTable(); detail(); renderLog(DATA.logTail);
if(DATA.live) setInterval(poll, 5000);
</script></body></html>
"""
