"""
Shared database connection helper for TRUEFAM reports.
Reads PRODUCTION_DATABASE_URL from the project .env and returns a read-only
psycopg2 connection (SSL required).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# ── Load .env from project root ------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / "truefam-welfare-backend" / ".env")
except ImportError:
    pass

import warnings
warnings.filterwarnings("ignore", message=".*pandas only supports SQLAlchemy.*")

import psycopg2
import pandas as pd


def _parse_url(url: str) -> dict:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return dict(
        host=parsed.hostname,
        port=parsed.port or 25060,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username,
        password=parsed.password,
        sslmode=qs.get("sslmode", ["require"])[0],
    )


def get_connection():
    """Return a read-only psycopg2 connection to the production database."""
    url = os.getenv("PRODUCTION_DATABASE_URL")
    if not url:
        print("ERROR: PRODUCTION_DATABASE_URL is not set in .env", file=sys.stderr)
        sys.exit(1)

    params = _parse_url(url)
    conn = psycopg2.connect(**params)
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only = ON;")
    conn.commit()
    return conn


def query(sql: str) -> pd.DataFrame:
    """Execute a read-only SQL query and return a pandas DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()
