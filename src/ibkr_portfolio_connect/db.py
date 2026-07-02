"""SQLite data layer (SQLModel) — the boundary between the web and the worker.

The web process is READ-ONLY for trade data: it lists runs/orders/events and it
may insert a *job request* (a row in `job`). It never holds broker credentials
and never places orders. The separate worker process (which DOES hold IBKR +
bbterminal creds) claims requested jobs, runs the rebalance, and writes the
RunSummary / OrderLog / Event rows back.

SQLite in WAL mode is the right fit for a single-node RPi4: one writer (the
worker) + many concurrent readers (the web) with no separate DB server. Set
MOMENTUM_DB_PATH to relocate the file (default: data/momentum.db).
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, col, create_engine, select

# ─── job lifecycle ────────────────────────────────────────────────────────────
JOB_REQUESTED = "requested"  # web created it; worker hasn't picked it up
JOB_CLAIMED = "claimed"      # worker took ownership
JOB_RUNNING = "running"      # rebalance in progress
JOB_DONE = "done"
JOB_ERROR = "error"

# ─── job kinds (what the worker should do with the job) ───────────────────────
JOB_KIND_REBALANCE = "rebalance"          # run the bbterminal->IBKR rebalance
JOB_KIND_MAPPING = "mapping_refresh"      # refresh data/mapping_snapshot.json
JOB_KIND_PORTFOLIO = "portfolio_refresh"  # refresh data/portfolio_snapshot.json
JOB_KIND_STRATEGIES = "strategies_refresh"  # refresh data/strategies_snapshot.json
JOB_KIND_ORDER_PREVIEW = "order_preview"  # what-if a single manual buy (no order)
JOB_KIND_ORDER_PLACE = "order_place"      # place a single manual buy (real order)
JOB_KIND_BATCH_PREVIEW = "batch_preview"  # what-if a whole-strategy buy (no orders)
JOB_KIND_BATCH_PLACE = "batch_place"      # place a whole-strategy buy, one by one

# ─── single-order (manual test-buy) ticket lifecycle ──────────────────────────
TICKET_REQUESTED = "requested"   # created by web; worker will what-if it
TICKET_PREVIEWED = "previewed"   # what-if done; awaiting the user's typed confirm
TICKET_BLOCKED = "blocked"       # sizing/safety refused it (e.g. below one share)
TICKET_CONFIRMED = "confirmed"   # user typed EXECUTE; worker will place it
TICKET_PLACING = "placing"       # worker is submitting the order
TICKET_PLACED = "placed"         # order submitted (see order_id / place_json)
TICKET_FAILED = "failed"         # placement raised (see error)

# ─── run status (mirrors run_record constants) ────────────────────────────────
RUN_RUNNING = "running"
RUN_DRY_RUN = "dry_run"
RUN_SUCCESS = "success"
RUN_PARTIAL = "partial"
RUN_FAILED = "failed"
RUN_ABORTED = "aborted"
RUN_ERROR = "error"


def _now() -> datetime:
    return datetime.now(UTC)


class Job(SQLModel, table=True):
    """A request to run the monthly rebalance. Written by the web (status
    'requested'); the worker is the only thing that may execute it."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    kind: str = "rebalance"
    dry_run: bool = True
    status: str = Field(default=JOB_REQUESTED, index=True)
    requested_by: str = "web"
    note: str = ""
    claimed_at: datetime | None = None
    finished_at: datetime | None = None
    run_id: int | None = Field(default=None, foreign_key="runsummary.id")
    error: str = ""
    payload: str = ""  # optional JSON params (e.g. {"ticket_id": 7} for order jobs)


class RunSummary(SQLModel, table=True):
    """One rebalance run — the headline row for the runs list and charts."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    finished_at: datetime | None = None
    job_id: int | None = Field(default=None, foreign_key="job.id")
    strategy_id: int | None = None
    strategy_name: str = ""
    as_of_date: str = ""
    dry_run: bool = True
    status: str = Field(default=RUN_RUNNING, index=True)
    nav_eur: float | None = None
    n_trades: int = 0
    n_success: int = 0
    n_failed: int = 0
    total_slippage_eur: float | None = None
    total_commission_eur: float | None = None
    total_cost_pct: float | None = None
    aborted_reason: str = ""
    gate_json: str = ""  # health / freshness snapshot, JSON text


class OrderLog(SQLModel, table=True):
    """Per-order execution + slippage detail for a run."""

    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="runsummary.id", index=True)
    conid: int | None = None
    symbol: str = ""
    exchange: str = ""
    side: str = ""
    quantity: float = 0.0
    reference_price: float | None = None
    fill_price: float | None = None
    slippage_pct: float | None = None
    slippage_eur: float | None = None
    commission: float | None = None
    currency: str = ""
    status: str = ""
    error: str = ""


class Event(SQLModel, table=True):
    """Append-only event stream (mirrors the ntfy notifications)."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    run_id: int | None = Field(default=None, foreign_key="runsummary.id", index=True)
    level: str = "info"
    title: str = ""
    body: str = ""


class OrderTicket(SQLModel, table=True):
    """A single manual test-buy, sized as a % of NAV, that the user previews
    (IBKR what-if) and then explicitly confirms before the worker places it.

    Distinct from the rebalance path: one instrument, MKT DAY, no strategy
    targets. `status` walks the TICKET_* lifecycle; the web only ever creates
    it and flips it to CONFIRMED — the worker owns every IBKR call."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    status: str = Field(default=TICKET_REQUESTED, index=True)
    requested_by: str = "web"
    batch_id: int | None = Field(default=None, foreign_key="orderbatch.id", index=True)
    weight: float = 0.0             # strategy target weight (batch buys); 0 for a lone buy
    # what to buy
    strategy_id: int | None = None
    conid: int = 0
    symbol: str = ""
    name: str = ""
    currency: str = ""              # instrument's local currency
    listing_exchange: str = ""
    side: str = "BUY"
    # sizing
    pct_of_nav: float = 0.0         # user-chosen size, % of portfolio NAV
    nav_eur: float | None = None    # NAV used, fetched live at preview time
    price_eur_ref: float | None = None  # bbterminal entry price in EUR (share-count ref)
    ref_price_local: float | None = None  # bbterminal entry price in the local ccy (slippage ref)
    target_eur: float | None = None     # nav_eur * pct/100
    quantity: float | None = None       # resolved shares (fractional or whole)
    fractional: bool = False
    # preview / placement results
    est_cost_eur: float | None = None
    commission: float | None = None
    fill_price: float | None = None     # avg execution price (local ccy), from order_status
    slippage_pct: float | None = None   # signed: +% = paid above bbterminal ref (a cost)
    slippage_eur: float | None = None   # slippage in EUR (pct x reference cost)
    preview_json: str = ""
    place_json: str = ""
    order_id: str = ""
    error: str = ""


class OrderBatch(SQLModel, table=True):
    """A whole-strategy buy: one OrderTicket per holding, sized by weight, all
    previewed then placed sequentially. Reuses the TICKET_* lifecycle for its
    own `status` (requested→previewed→confirmed→placing→placed); the per-holding
    outcome lives on each child ticket."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    status: str = Field(default=TICKET_REQUESTED, index=True)
    requested_by: str = "web"
    strategy_id: int | None = None
    strategy_name: str = ""
    total_pct: float = 0.0          # total % of NAV to deploy across the weights
    nav_eur: float | None = None
    error: str = ""


# ─── engine / session ─────────────────────────────────────────────────────────


def default_db_path() -> Path:
    return Path(os.environ.get("MOMENTUM_DB_PATH", "data/momentum.db"))


_engine: Engine | None = None


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection: Any, _connection_record: Any) -> None:
    """WAL = concurrent readers (web) while the single writer (worker) commits."""
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA synchronous=NORMAL")
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


def get_engine(db_path: Path | None = None) -> Engine:
    global _engine
    if _engine is None:
        path = db_path or default_db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{path}", connect_args={"check_same_thread": False}
        )
    return _engine


def init_db(db_path: Path | None = None) -> Engine:
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
    _migrate(engine)
    return engine


def _migrate(engine: Engine) -> None:
    """Tiny additive migrations for DBs created before a column existed —
    create_all() never ALTERs an existing table. Idempotent."""
    from sqlalchemy import text
    with engine.begin() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(job)"))}
        if cols and "kind" not in cols:
            conn.execute(text("ALTER TABLE job ADD COLUMN kind VARCHAR DEFAULT 'rebalance'"))
        if cols and "payload" not in cols:
            conn.execute(text("ALTER TABLE job ADD COLUMN payload VARCHAR DEFAULT ''"))
        # OrderTicket gained batch grouping after its first release.
        tcols = {row[1] for row in conn.execute(text("PRAGMA table_info(orderticket)"))}
        if tcols and "batch_id" not in tcols:
            conn.execute(text("ALTER TABLE orderticket ADD COLUMN batch_id INTEGER"))
        if tcols and "weight" not in tcols:
            conn.execute(text("ALTER TABLE orderticket ADD COLUMN weight FLOAT DEFAULT 0"))
        for c in ("ref_price_local", "fill_price", "slippage_pct", "slippage_eur"):
            if tcols and c not in tcols:
                conn.execute(text(f"ALTER TABLE orderticket ADD COLUMN {c} FLOAT"))


@contextmanager
def get_session(db_path: Path | None = None) -> Iterator[Session]:
    with Session(get_engine(db_path)) as session:
        yield session


# ─── repository helpers (used by both web and worker) ─────────────────────────


def request_job(session: Session, *, dry_run: bool = True, kind: str = JOB_KIND_REBALANCE,
                requested_by: str = "web", note: str = "", payload: str = "") -> Job:
    job = Job(kind=kind, dry_run=dry_run, requested_by=requested_by, note=note, payload=payload)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


# ─── single-order tickets ─────────────────────────────────────────────────────


def create_order_ticket(session: Session, **fields: Any) -> OrderTicket:
    """Web side: record a manual buy request (status REQUESTED) to what-if."""
    ticket = OrderTicket(**fields)
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def get_order_ticket(session: Session, ticket_id: int) -> OrderTicket | None:
    return session.get(OrderTicket, ticket_id)


def save_order_ticket(session: Session, ticket: OrderTicket) -> OrderTicket:
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def list_order_tickets(session: Session, limit: int = 20) -> list[OrderTicket]:
    return list(session.exec(
        select(OrderTicket).order_by(col(OrderTicket.created_at).desc()).limit(limit)
    ))


def placed_order_tickets(session: Session) -> list[OrderTicket]:
    """Every PLACED buy, oldest first — the append-only attribution ledger the
    per-strategy positions view aggregates (Option B: logical separation)."""
    return list(session.exec(
        select(OrderTicket).where(OrderTicket.status == TICKET_PLACED)
        .order_by(col(OrderTicket.created_at))
    ))


def create_order_batch(session: Session, **fields: Any) -> OrderBatch:
    batch = OrderBatch(**fields)
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return batch


def get_order_batch(session: Session, batch_id: int) -> OrderBatch | None:
    return session.get(OrderBatch, batch_id)


def save_order_batch(session: Session, batch: OrderBatch) -> OrderBatch:
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return batch


def tickets_for_batch(session: Session, batch_id: int) -> list[OrderTicket]:
    """A batch's child tickets in stable creation order (= weight order as
    added), so the overview and sequential placement march the same list."""
    return list(session.exec(
        select(OrderTicket).where(OrderTicket.batch_id == batch_id)
        .order_by(col(OrderTicket.id))
    ))


def reset_orphaned_jobs(session: Session) -> int:
    """Worker-startup recovery. A job left CLAIMED/RUNNING (or an OrderTicket /
    OrderBatch left PLACING) means the worker died mid-flight — e.g. a dev
    hot-restart. Mark them errored/failed rather than re-running them (a trade
    may have partly executed), so they don't wedge the queue or leave a page
    stuck on 'refreshing…'. Returns how many jobs were cleared."""
    n = 0
    for job in session.exec(select(Job).where(col(Job.status).in_((JOB_CLAIMED, JOB_RUNNING)))):
        job.status = JOB_ERROR
        job.error = job.error or "worker restarted before this job finished"
        job.finished_at = _now()
        session.add(job)
        n += 1
    for t in session.exec(select(OrderTicket).where(OrderTicket.status == TICKET_PLACING)):
        t.status = TICKET_FAILED
        t.error = t.error or "worker restarted mid-placement — verify this order in IBKR"
        session.add(t)
    for b in session.exec(select(OrderBatch).where(OrderBatch.status == TICKET_PLACING)):
        b.status = TICKET_FAILED
        b.error = b.error or "worker restarted mid-placement"
        session.add(b)
    session.commit()
    return n


def claim_next_job(session: Session) -> Job | None:
    """Worker side: atomically take the oldest requested job."""
    job = session.exec(
        select(Job).where(Job.status == JOB_REQUESTED).order_by(col(Job.created_at))
    ).first()
    if job is None:
        return None
    job.status = JOB_CLAIMED
    job.claimed_at = _now()
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def list_jobs(session: Session, limit: int = 50) -> list[Job]:
    return list(
        session.exec(select(Job).order_by(col(Job.created_at).desc()).limit(limit))
    )


def list_runs(session: Session, limit: int = 100) -> list[RunSummary]:
    return list(
        session.exec(
            select(RunSummary).order_by(col(RunSummary.created_at).desc()).limit(limit)
        )
    )


def get_run(session: Session, run_id: int) -> RunSummary | None:
    return session.get(RunSummary, run_id)


def orders_for_run(session: Session, run_id: int) -> list[OrderLog]:
    return list(session.exec(select(OrderLog).where(OrderLog.run_id == run_id)))


def events_for_run(session: Session, run_id: int) -> list[Event]:
    return list(
        session.exec(
            select(Event).where(Event.run_id == run_id).order_by(col(Event.created_at))
        )
    )


def recent_events(session: Session, limit: int = 100) -> list[Event]:
    return list(
        session.exec(select(Event).order_by(col(Event.created_at).desc()).limit(limit))
    )
