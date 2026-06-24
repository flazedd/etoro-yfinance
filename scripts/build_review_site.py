"""Generate a self-contained mapping-review web page.

Merges the resolution + verification + liquidity data into one static HTML file
(no server, no deps — just open it in a browser). The page lets you eyeball each
bbterminal->IBKR mapping, sorted worst-confidence-first among liquid names, and
record an approve/reject decision per company (autosaved in the browser, with
JSON export/import).

    uv run python scripts/build_review_site.py
    open data/leonteq_review.html

Why a static page: it needs nothing running, works offline, and its only output
is a decisions JSON you can re-ingest — matching the conid_map review philosophy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DATA_DIR = Path("data")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default="leonteq")
    parser.add_argument("--min-adv", type=float, default=1_000_000,
                        help="default liquidity threshold shown in the page (EUR ADV)")
    args = parser.parse_args()

    res = _load(DATA_DIR / f"{args.slug}_ibkr_resolution.json").get("results", {})
    # company_id -> country, for the GuruFocus link (US exchanges = ticker only).
    uni = _load(DATA_DIR / f"{args.slug}_universe.json").get("members", [])
    country_by_cid = {str(m.get("company_id")): m.get("country") for m in uni}
    ver = _load(DATA_DIR / f"{args.slug}_mapping_verification.json").get("results", {})
    liq = _load(DATA_DIR / f"{args.slug}_liquidity.json").get("results", {})
    fig = _load(DATA_DIR / f"{args.slug}_openfigi.json").get("results", {})
    exc = _load(DATA_DIR / f"{args.slug}_exclusions.json").get("exclusions", {})
    if not res:
        print("no resolution file — run scripts/resolve_universe.py first", file=sys.stderr)
        return 1

    rows = []
    for cid, r in res.items():
        if r.get("status") != "resolved" or not r.get("conid"):
            continue
        v = ver.get(cid, {})
        lq = liq.get(cid, {})
        fg = fig.get(cid, {})
        rows.append({
            "cid": cid,
            "bb": r.get("company_name"),
            "ibkr": v.get("ibkr_name"),
            "figi": fg.get("verdict"),
            "figi_name": fg.get("figi_name"),
            "score": v.get("name_score"),
            "conf": v.get("confidence") or "?",
            "method": r.get("method"),
            "ccy": r.get("currency"),
            "ibkr_ccy": v.get("ibkr_ccy"),
            "ccy_ok": v.get("ccy_ok", True),
            "ticker": r.get("ticker"),
            "ibkr_sym": v.get("ibkr_symbol") or r.get("ibkr_symbol"),
            "tmatch": v.get("ticker_match"),
            "lmatch": v.get("listing_match"),
            "exch": r.get("exchange"),
            "conid": r.get("conid"),
            "listing": r.get("ibkr_listing") or v.get("ibkr_listing"),
            "isin": r.get("isin"),
            "adv": lq.get("adv_eur"),
            "country": country_by_cid.get(cid),
        })

    payload = {
        "slug": args.slug,
        "minAdv": args.min_adv,
        "rows": rows,
        "excluded": [{"cid": k, **val} for k, val in exc.items()],
    }
    html = _HTML.replace("/*__DATA__*/", json.dumps(payload))
    out = DATA_DIR / f"{args.slug}_review.html"
    out.write_text(html)
    n_adv = sum(1 for r in rows if r["adv"])
    print(f"wrote {out}  ({len(rows)} mappings, {n_adv} with ADV, {len(exc)} excluded)")
    print(f"open it:  open {out}")
    return 0


# The page: vanilla JS, embedded data, localStorage-backed decisions. No deps.
_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>bbterminal -> IBKR mapping review</title>
<style>
 :root{--g:#137333;--y:#b06000;--r:#c5221f;--bg:#f6f7f9;--line:#e3e6ea}
 *{box-sizing:border-box} body{font:13px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:var(--bg);color:#1f2328}
 header{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);padding:10px 16px;z-index:5}
 h1{font-size:15px;margin:0 0 8px} .ctrls{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
 .ctrls label{font-size:12px;color:#555} input,select{font:inherit;padding:3px 6px;border:1px solid #ccc;border-radius:5px}
 .stat{display:inline-block;padding:2px 8px;border-radius:10px;background:#eef;margin-right:6px;font-size:12px}
 button{font:inherit;border:1px solid #ccc;background:#fff;border-radius:6px;padding:3px 9px;cursor:pointer}
 button:hover{background:#f0f0f0}
 table{border-collapse:collapse;width:100%;background:#fff} th,td{padding:5px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
 th{position:sticky;top:var(--hh,110px);z-index:4;background:#fafbfc;cursor:pointer;user-select:none;white-space:nowrap;box-shadow:0 1px 0 var(--line)}
 th:hover{background:#eef}
 tr.dim{opacity:.4} tr.approve{background:#e9f6ee} tr.reject{background:#fde9e8}
 .name{max-width:340px} .sub{color:#888;font-size:11px}
 .pill{padding:1px 7px;border-radius:9px;font-size:11px;font-weight:600;color:#fff}
 .high{background:var(--g)} .medium{background:var(--y)} .low{background:var(--r)} .miss{background:#666}
 .num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
 .bad{color:var(--r);font-weight:600} .ok{color:var(--g);font-weight:600} .mono{font-family:ui-monospace,Menlo,monospace;font-size:11px}
 .act button{padding:2px 7px;margin-right:3px} .on-a{background:var(--g);color:#fff;border-color:var(--g)}
 .on-r{background:var(--r);color:#fff;border-color:var(--r)}
 a{color:#1a56db;text-decoration:none} a:hover{text-decoration:underline}
 .src{font-size:9px;font-weight:700;padding:0 4px;border-radius:6px;margin-left:5px;letter-spacing:.3px;vertical-align:middle}
 .src-bb{background:#dbeafe;color:#1e40af} .src-ibkr{background:#ffedd5;color:#9a3412}
 .src-calc{background:#ede9fe;color:#5b21b6} .src-you{background:#dcfce7;color:#166534}
 .src-mix{background:#e5e7eb;color:#374151} .src-figi{background:#ccfbf1;color:#0f766e}
 .leg{font-size:11px;color:#666}
 .fv{padding:1px 6px;border-radius:9px;font-size:10px;font-weight:700;white-space:nowrap}
 .fv-triple_match{background:#137333;color:#fff} .fv-isin_identity_ok{background:#1a56db;color:#fff}
 .fv-ticker_conflict{background:#c5221f;color:#fff} .fv-ibkr_figi_mismatch{background:#c5221f;color:#fff}
 .fv-no_figi{background:#e5e7eb;color:#666}
</style></head><body>
<header>
 <h1>bbterminal &rarr; IBKR mapping review &mdash; <span id="slug"></span></h1>
 <div class="ctrls">
  <span><span class="stat" id="s-total"></span><span class="stat" id="s-trade"></span>
   <span class="stat" style="background:#e9f6ee" id="s-app"></span>
   <span class="stat" style="background:#fde9e8" id="s-rej"></span>
   <span class="stat" id="s-pend"></span></span>
  <label>Min ADV (EUR/day) <input id="minadv" type="number" step="100000" style="width:120px"></label>
  <label><input id="hideilliq" type="checkbox" checked> hide below-threshold</label>
  <label>Confidence <select id="fconf"><option value="">all</option><option>low</option>
    <option value="lowmed">low+medium</option></select></label>
  <label>Decision <select id="fdec"><option value="">all</option><option>pending</option>
    <option>approve</option><option>reject</option></select></label>
  <label>Search <input id="q" placeholder="name / ticker"></label>
  <button id="export">Export decisions</button>
  <label style="cursor:pointer">Import <input id="import" type="file" accept="application/json" hidden></label>
 </div>
 <div class="leg" style="margin-top:6px">source: <span class="src src-bb">BB</span>bbterminal
  <span class="src src-ibkr">IB</span>IBKR <span class="src src-figi">FIGI</span>OpenFIGI
  <span class="src src-mix">MIX</span>both <span class="src src-calc">CALC</span>computed
  <span class="src src-you">YOU</span>your input</div>
</header>
<table><thead><tr id="head"></tr></thead><tbody id="body"></tbody></table>
<script>
const DATA = /*__DATA__*/;
const LS = 'mapreview_'+DATA.slug;
let decisions = JSON.parse(localStorage.getItem(LS)||'{}');
const COLS = [
 {k:'_pri',t:'!',s:'calc'},{k:'_act',t:'decision',s:'you'},{k:'bb',t:'company name',s:'bb'},
 {k:'ibkr',t:'company name',s:'ibkr'},{k:'figi',t:'OpenFIGI verdict',s:'figi'},{k:'score',t:'name match',s:'calc'},{k:'conf',t:'conf',s:'calc'},
 {k:'adv',t:'ADV €/day',s:'mix'},{k:'method',t:'via',s:'calc'},{k:'ccy',t:'ccy',s:'bb'},
 {k:'ticker',t:'ticker',s:'bb'},{k:'exch',t:'exch',s:'bb'},{k:'listing',t:'listing',s:'ibkr'},
 {k:'conid',t:'conid',s:'ibkr'},{k:'isin',t:'isin',s:'bb'}
];
const SRCLBL={bb:'BB',ibkr:'IB',calc:'CALC',you:'YOU',mix:'MIX',figi:'FIGI'};
const FVTXT={triple_match:'✓✓✓ all agree',isin_identity_ok:'✓ ISIN ok / name diff',ticker_conflict:'⚠ class/ticker conflict',ibkr_figi_mismatch:'⚠ FIGI≠IBKR',no_figi:'no FIGI'};
let sort={k:'score',dir:1};   // worst (lowest) score first
const fmt=n=> n==null?'':Math.round(n).toLocaleString();
const adv=r=> r.adv==null?-1:r.adv;
function tradeable(r){const m=+document.getElementById('minadv').value; return r.adv!=null && r.adv>=m;}
function priority(r){ // lower = check sooner: liquid + low score on top
 const t=tradeable(r)?0:1; const s=(r.score==null?0:r.score); return t*10+s; }
function head(){
 document.getElementById('head').innerHTML=COLS.map(c=>`<th data-k="${c.k}">${c.t}<span class="src src-${c.s}">${SRCLBL[c.s]}</span></th>`).join('');
 document.querySelectorAll('th').forEach(th=>th.onclick=()=>{
   const k=th.dataset.k; if(k==='_act')return;
   sort.dir = sort.k===k? -sort.dir : 1; sort.k=k; render(); });
}
function val(r,k){ if(k==='_pri')return priority(r); if(k==='adv')return adv(r); return r[k]; }
function render(){
 const m=+document.getElementById('minadv').value, hide=document.getElementById('hideilliq').checked;
 const fc=document.getElementById('fconf').value, fd=document.getElementById('fdec').value;
 const q=document.getElementById('q').value.toLowerCase();
 let rows=DATA.rows.filter(r=>{
   if(hide && !tradeable(r)) return false;
   if(fc==='low' && r.conf!=='low') return false;
   if(fc==='lowmed' && !(r.conf==='low'||r.conf==='medium')) return false;
   const d=(decisions[r.cid]||{}).d||'pending';
   if(fd==='pending'&&d!=='pending')return false; if(fd&&fd!=='pending'&&d!==fd)return false;
   if(q && !((r.bb||'')+' '+(r.ibkr||'')+' '+(r.ticker||'')).toLowerCase().includes(q))return false;
   return true; });
 rows.sort((a,b)=>{let x=val(a,sort.k),y=val(b,sort.k);
   if(x==null)x=-Infinity; if(y==null)y=-Infinity;
   if(typeof x==='string')return sort.dir*x.localeCompare(y); return sort.dir*((x>y)-(x<y));});
 const body=document.getElementById('body');
 body.innerHTML=rows.map(r=>{
   const d=(decisions[r.cid]||{}).d||'pending';
   const pr=priority(r);
   const flag = r.conf==='low'?'●': (r.conf==='medium'?'◐':'');
   const ccyHtml = r.ccy_ok? r.ccy : `<span class="bad">${r.ccy}≠${r.ibkr_ccy||'?'}</span>`;
   const g=`https://www.google.com/search?q=${encodeURIComponent((r.isin||'')+' '+(r.ibkr||r.bb||''))}`;
   const ib=`https://www.interactivebrokers.ie/portal/?loginType=1&action=ACCT_MGMT_MAIN&clt=0#/quote/${r.conid}`;
   const gfsym = r.country==='United States' ? r.ticker : `${r.exch}:${r.ticker}`;
   const gf=`https://www.gurufocus.com/stock/${encodeURIComponent(gfsym)}/summary`;
   const tkHtml = r.ibkr_sym ? (r.tmatch
       ? ' <span class="ok" title="IBKR symbol matches">✓</span>'
       : ` <span class="bad" title="IBKR symbol differs">≠${r.ibkr_sym}</span>`) : '';
   const lmHtml = r.lmatch===false ? ' <span class="bad" title="not on expected venue">≠</span>'
       : (r.lmatch===true ? ' <span class="ok" title="on expected venue">✓</span>' : '');
   return `<tr class="${tradeable(r)?'':'dim'} ${d}">
    <td title="priority ${pr.toFixed(2)}" style="color:${r.conf==='low'?'var(--r)':r.conf==='medium'?'var(--y)':'#bbb'}">${flag}</td>
    <td class="act"><button data-c="${r.cid}" data-d="approve" class="${d==='approve'?'on-a':''}">✓</button>
        <button data-c="${r.cid}" data-d="reject" class="${d==='reject'?'on-r':''}">✗</button></td>
    <td class="name">${r.bb||''} <a href="${gf}" target="_blank" rel="noopener" title="GuruFocus ${gfsym}">GF⇗</a><div class="sub">${r.ticker} · ${r.exch}</div></td>
    <td class="name">${r.ibkr||'<span class=bad>(no IBKR name)</span>'} <a href="${g}" target="_blank" title="verify">⇗</a></td>
    <td>${r.figi?`<span class="fv fv-${r.figi}" title="OpenFIGI name: ${(r.figi_name||'').replace(/"/g,'&quot;')}">${FVTXT[r.figi]||r.figi}</span>`:'<span class=sub>—</span>'}</td>
    <td class="num"><span class="pill ${r.conf}">${r.score==null?'?':r.score.toFixed(2)}</span></td>
    <td>${r.conf}</td>
    <td class="num">${r.adv==null?'<span class=sub>n/a</span>':fmt(r.adv)}</td>
    <td>${r.method||''}</td><td class="num">${ccyHtml}</td>
    <td>${r.ticker}${tkHtml}</td><td>${r.exch}</td><td>${r.listing||''}${lmHtml}</td>
    <td class="num mono"><a href="${ib}" target="_blank" rel="noopener" title="IBKR contract info">${r.conid}</a></td>
    <td class="mono">${r.isin||''}</td></tr>`;
 }).join('');
 body.querySelectorAll('button[data-c]').forEach(b=>b.onclick=()=>{
   const c=b.dataset.c, dd=b.dataset.d;
   decisions[c]=((decisions[c]||{}).d===dd)?{}:{d:dd};
   localStorage.setItem(LS,JSON.stringify(decisions)); render(); });
 stats();
}
function stats(){
 const m=+document.getElementById('minadv').value;
 const tr=DATA.rows.filter(tradeable).length;
 let a=0,rj=0; for(const k in decisions){if(decisions[k].d==='approve')a++;if(decisions[k].d==='reject')rj++;}
 document.getElementById('s-total').textContent=DATA.rows.length+' mappings';
 document.getElementById('s-trade').textContent=tr+' tradeable (≥ ADV)';
 document.getElementById('s-app').textContent=a+' approved';
 document.getElementById('s-rej').textContent=rj+' rejected';
 document.getElementById('s-pend').textContent=(tr-a-rj>=0?tr-a-rj:'')+' pending (tradeable)';
}
document.getElementById('slug').textContent=DATA.slug;
document.getElementById('minadv').value=DATA.minAdv;
['minadv','hideilliq','fconf','fdec','q'].forEach(id=>{
 const el=document.getElementById(id); el.addEventListener(el.type==='checkbox'||el.tagName==='SELECT'?'change':'input',render);});
document.getElementById('export').onclick=()=>{
 const blob=new Blob([JSON.stringify({slug:DATA.slug,decisions},null,2)],{type:'application/json'});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=DATA.slug+'_review_decisions.json';a.click();};
document.getElementById('import').onchange=e=>{const f=e.target.files[0];if(!f)return;
 f.text().then(t=>{const j=JSON.parse(t);decisions=j.decisions||j;localStorage.setItem(LS,JSON.stringify(decisions));render();});};
// Keep the column-header sticky offset exactly equal to the toolbar height,
// even when the controls wrap onto more rows (otherwise data slides under it).
function setHH(){const h=document.querySelector('header').offsetHeight;
 document.documentElement.style.setProperty('--hh',h+'px');}
addEventListener('resize',setHH);
head(); render(); setHH();
</script></body></html>
"""


if __name__ == "__main__":
    sys.exit(main())
