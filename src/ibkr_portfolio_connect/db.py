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
    return engine


@contextmanager
def get_session(db_path: Path | None = None) -> Iterator[Session]:
    with Session(get_engine(db_path)) as session:
        yield session


# ─── repository helpers (used by both web and worker) ─────────────────────────


def request_job(session: Session, *, dry_run: bool, requested_by: str = "web",
                note: str = "") -> Job:
    job = Job(dry_run=dry_run, requested_by=requested_by, note=note)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


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
