"""Read-only FastAPI + HTMX web app for the momentum stack.

Three pages:
  * /universe     — the LEONTEQ universe and its IBKR mapping (from data/*.json)
  * /execution    — request + monitor the monthly rebalance (jobs -> worker -> DB)
  * /performance  — bbterminal strategy performance (from a published snapshot)

This package holds NO broker credentials. It reads the universe data artifacts,
reads a performance snapshot file (produced by the credentialed publisher), and
reads/writes the SQLite job + run tables. Actual trading is done by the separate
worker process (see web/worker.py).
"""
