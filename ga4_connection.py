"""
GA4 Data API helper for TRUEFAM web analytics reports.
Pulls data from Google Analytics 4 using a service account.
Falls back to empty/placeholder DataFrames when credentials are not configured.
"""

from __future__ import annotations

import os
import sys
import warnings
from datetime import date, timedelta
from pathlib import Path

warnings.filterwarnings("ignore", message=".*pandas only supports SQLAlchemy.*")

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / "truefam-welfare-backend" / ".env")
except ImportError:
    pass

import pandas as pd

# ── GA4 configuration ────────────────────────────────────────────────────────
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "")
GA4_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# Default date range: last 28 days
DEFAULT_START = (date.today() - timedelta(days=28)).isoformat()
DEFAULT_END = (date.today() - timedelta(days=1)).isoformat()


def _ga4_available() -> bool:
    """Check if GA4 credentials and property ID are configured."""
    return bool(GA4_PROPERTY_ID) and bool(GA4_CREDENTIALS) and Path(GA4_CREDENTIALS).exists()


def _get_client():
    """Create a GA4 BetaAnalyticsDataClient."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GA4_CREDENTIALS
    return BetaAnalyticsDataClient()


def run_report(
    dimensions: list[str],
    metrics: list[str],
    start_date: str = DEFAULT_START,
    end_date: str = DEFAULT_END,
    dimension_filter=None,
    order_bys=None,
    limit: int = 10000,
) -> pd.DataFrame:
    """
    Run a GA4 report and return a pandas DataFrame.

    If GA4 credentials are not configured, returns an empty DataFrame
    with the requested column names so the report renders gracefully.
    """
    columns = dimensions + metrics

    if not _ga4_available():
        return pd.DataFrame(columns=columns)

    try:
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )

        client = _get_client()

        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=limit,
        )

        if dimension_filter:
            request.dimension_filter = dimension_filter
        if order_bys:
            request.order_bys = order_bys

        response = client.run_report(request)

        rows = []
        for row in response.rows:
            r = {}
            for i, dim in enumerate(dimensions):
                r[dim] = row.dimension_values[i].value
            for i, met in enumerate(metrics):
                val = row.metric_values[i].value
                try:
                    r[met] = float(val)
                except ValueError:
                    r[met] = val
            rows.append(r)

        return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)

    except Exception as e:
        print(f"GA4 API error: {e}", file=sys.stderr)
        return pd.DataFrame(columns=columns)


def get_headline_kpis(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> dict:
    """Fetch headline KPIs for the executive snapshot."""
    df = run_report(
        dimensions=[],
        metrics=[
            "totalUsers", "newUsers", "sessions", "engagedSessions",
            "averageSessionDuration", "bounceRate", "engagementRate",
            "screenPageViews", "eventCount", "conversions",
        ],
        start_date=start_date,
        end_date=end_date,
    )

    if df.empty:
        return {
            "totalUsers": 0, "newUsers": 0, "sessions": 0,
            "engagedSessions": 0, "averageSessionDuration": 0.0,
            "bounceRate": 0.0, "engagementRate": 0.0,
            "screenPageViews": 0, "eventCount": 0, "conversions": 0,
        }

    return df.iloc[0].to_dict()


def get_traffic_by_channel(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> pd.DataFrame:
    """Fetch session data grouped by default channel."""
    return run_report(
        dimensions=["sessionDefaultChannelGroup"],
        metrics=["sessions", "engagedSessions", "engagementRate", "conversions"],
        start_date=start_date,
        end_date=end_date,
    )


def get_traffic_over_time(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> pd.DataFrame:
    """Fetch daily session counts."""
    return run_report(
        dimensions=["date"],
        metrics=["sessions", "totalUsers", "newUsers"],
        start_date=start_date,
        end_date=end_date,
    )


def get_top_pages(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END, limit: int = 10) -> pd.DataFrame:
    """Fetch top pages by pageviews."""
    return run_report(
        dimensions=["pagePath", "pageTitle"],
        metrics=["screenPageViews", "engagementRate", "averageSessionDuration"],
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


def get_geo_data(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> pd.DataFrame:
    """Fetch geographic data by country."""
    return run_report(
        dimensions=["country"],
        metrics=["totalUsers", "sessions", "engagementRate"],
        start_date=start_date,
        end_date=end_date,
    )


def get_device_data(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> pd.DataFrame:
    """Fetch device category breakdown."""
    return run_report(
        dimensions=["deviceCategory"],
        metrics=["totalUsers", "sessions"],
        start_date=start_date,
        end_date=end_date,
    )


def get_demographics(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> dict:
    """Fetch age and gender breakdown."""
    age_df = run_report(
        dimensions=["userAgeBracket"],
        metrics=["totalUsers"],
        start_date=start_date,
        end_date=end_date,
    )
    gender_df = run_report(
        dimensions=["userGender"],
        metrics=["totalUsers"],
        start_date=start_date,
        end_date=end_date,
    )
    return {"age": age_df, "gender": gender_df}


def get_funnel_data(start_date: str = DEFAULT_START, end_date: str = DEFAULT_END) -> list[dict]:
    """
    Fetch enrollment funnel step counts.
    Returns a list of dicts: [{step, label, count}, ...]
    """
    # Step 1: Sessions (session_start is automatic)
    sessions_df = run_report(
        dimensions=[], metrics=["sessions"],
        start_date=start_date, end_date=end_date,
    )
    sessions = int(sessions_df["sessions"].iloc[0]) if not sessions_df.empty else 0

    # Steps 2-6: Custom events
    event_steps = [
        ("Enrollment Page View", "page_view"),  # filtered by path in real impl
        ("Application Initiated", "apply_now_click"),
        ("Nationality Selected", "nationality_selected"),
        ("Form Submitted", "form_submit"),
        ("Membership Confirmed", "membership_confirmed"),
    ]

    funnel = [{"step": 1, "label": "Site Entry", "count": sessions}]

    for i, (label, event_name) in enumerate(event_steps, 2):
        df = run_report(
            dimensions=["eventName"],
            metrics=["eventCount"],
            start_date=start_date,
            end_date=end_date,
        )
        # Filter for the specific event
        if not df.empty and event_name in df["eventName"].values:
            count = int(df.loc[df["eventName"] == event_name, "eventCount"].iloc[0])
        else:
            count = 0
        funnel.append({"step": i, "label": label, "count": count})

    return funnel
