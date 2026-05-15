"""GA4 API helper module for the ga4-reporting-analyst skill.

Provides a reusable client and query functions for the 5 standard report types.
Loads credentials from ~/.agents/.env per the .api_registry convention.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)

# ---------------------------------------------------------------------------
# Environment & client setup
# ---------------------------------------------------------------------------

def _load_env():
    """Load GA4 env vars from ~/.agents/.env and resolve relative paths."""
    env_path = Path.home() / ".agents" / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    agents_dir = Path.home() / ".agents"
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip('"')

    if not cred_path:
        raise EnvironmentError(
            "GOOGLE_APPLICATION_CREDENTIALS not set in ~/.agents/.env"
        )

    # Resolve relative paths against ~/.agents/
    if not Path(cred_path).is_absolute():
        cred_path = str(agents_dir / cred_path)

    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Credentials file not found: {cred_path}")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
    return os.getenv("GA4_PROPERTY_ID", "").strip('"')


def get_client_and_property():
    """Return a (client, property_id) tuple ready for queries.

    Loads env on first call. Safe to call repeatedly — env loading is idempotent.
    """
    property_id = _load_env()
    if not property_id:
        raise EnvironmentError("GA4_PROPERTY_ID not set in ~/.agents/.env")
    client = BetaAnalyticsDataClient()
    return client, property_id


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def _run_report(client, property_id, date_ranges, dimensions=None, metrics=None, limit=None):
    """Low-level wrapper around RunReportRequest.

    When two date ranges are provided, the GA4 API adds a "dateRange" dimension
    and returns separate rows for each range. This function merges them so that
    metric values become [current_range_value, comparison_range_value] lists.
    """
    has_comparison = len(date_ranges) == 2

    dim_list = [Dimension(name=d) for d in (dimensions or [])]
    met_list = [Metric(name=m) for m in (metrics or [])]
    dr_list = [
        DateRange(start_date=dr["start_date"], end_date=dr["end_date"])
        for dr in date_ranges
    ]

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=dr_list,
        dimensions=dim_list,
        metrics=met_list,
    )
    if limit:
        request.limit = limit

    response = client.run_report(request)

    dim_names = [d.name for d in dim_list]
    met_names = [m.name for m in met_list]

    if has_comparison:
        # GA4 returns rows per dimension+dateRange combination.
        # The API adds a "dateRange" dimension with values "date_range_0" / "date_range_1".
        # For dimensions like unifiedPagePathScreen, values match across ranges → pair by key.
        # For dimensions like yearMonth, values differ → pair by position.
        # GA4 also returns zero-value artifact rows (e.g., 202503/date_range_0 with all zeros).
        # We filter those out and merge the real data into single rows with [current, comparison].
        range0_rows = []
        range1_rows = []
        for row in response.rows:
            dr_index = row.dimension_values[len(dim_names)].value
            dim_vals = tuple(row.dimension_values[i].value for i in range(len(dim_names)))
            met_vals = [row.metric_values[i].value for i in range(len(met_names))]
            entry = (dim_vals, met_vals)
            if dr_index == "date_range_0":
                range0_rows.append(entry)
            elif dr_index == "date_range_1":
                range1_rows.append(entry)

        # Filter out zero-value artifact rows
        range0_rows = [(d, m) for d, m in range0_rows if not all(v == "0" for v in m)]
        range1_rows = [(d, m) for d, m in range1_rows if not all(v == "0" for v in m)]

        # Build a lookup for range1 by dimension values (for same-key pairing)
        range1_by_dim = {dims: mets for dims, mets in range1_rows}

        rows = []
        for idx, (dim_vals, met_vals) in enumerate(range0_rows):
            record = {}
            for i, name in enumerate(dim_names):
                record[name] = dim_vals[i]
            if dim_vals in range1_by_dim:
                # Same dimension value in both ranges (e.g., same page path)
                comp_vals = range1_by_dim[dim_vals]
            elif idx < len(range1_rows):
                # Different dimension values (e.g., yearMonth) — pair by position
                comp_vals = range1_rows[idx][1]
            else:
                comp_vals = ["0"] * len(met_names)
            for i, name in enumerate(met_names):
                record[name] = [met_vals[i], comp_vals[i]]
            rows.append(record)
    else:
        rows = []
        for row in response.rows:
            record = {}
            for i, name in enumerate(dim_names):
                record[name] = row.dimension_values[i].value
            for i, name in enumerate(met_names):
                record[name] = row.metric_values[i].value
            rows.append(record)

    result = {
        "property_id": property_id,
        "date_ranges": date_ranges,
        "dimensions": dim_names,
        "metrics": met_names,
        "row_count": len(rows),
        "rows": rows,
    }
    if has_comparison:
        result["comparison"] = True
    return result


# ---------------------------------------------------------------------------
# 1. Monthly Traffic
# ---------------------------------------------------------------------------

def monthly_traffic(start_date, end_date, compare_start_date=None, compare_end_date=None):
    """Month-by-month traffic trend.

    Optionally compare against a second date range.
    When comparison dates are provided, metric values become
    [current, comparison] lists.

    Dimensions: yearMonth
    Metrics: totalUsers, newUsers, sessions
    """
    client, property_id = get_client_and_property()
    dr = [{"start_date": start_date, "end_date": end_date}]
    if compare_start_date and compare_end_date:
        dr.append({"start_date": compare_start_date, "end_date": compare_end_date})
    return _run_report(
        client,
        property_id,
        date_ranges=dr,
        dimensions=["yearMonth"],
        metrics=["totalUsers", "newUsers", "sessions"],
    )


# ---------------------------------------------------------------------------
# 2. Acquisition Channels
# ---------------------------------------------------------------------------

def acquisition_channels(start_date, end_date, compare_start_date=None, compare_end_date=None):
    """Where visitors come from by default channel group.

    Optionally compare against a second date range.

    Dimensions: firstUserPrimaryChannelGroup
    Metrics: totalUsers, newUsers, activeUsers,
             userEngagementDuration, engagedSessions, engagementRate
    """
    client, property_id = get_client_and_property()
    dr = [{"start_date": start_date, "end_date": end_date}]
    if compare_start_date and compare_end_date:
        dr.append({"start_date": compare_start_date, "end_date": compare_end_date})
    return _run_report(
        client,
        property_id,
        date_ranges=dr,
        dimensions=["firstUserPrimaryChannelGroup"],
        metrics=[
            "totalUsers",
            "newUsers",
            "activeUsers",
            "userEngagementDuration",
            "engagedSessions",
            "engagementRate",
        ],
    )


# ---------------------------------------------------------------------------
# 3. Top Traffic Pages
# ---------------------------------------------------------------------------

def top_traffic_pages(start_date, end_date, limit=20, compare_start_date=None, compare_end_date=None):
    """Which pages get the most traffic.

    Optionally compare against a second date range.

    Dimensions: unifiedPagePathScreen
    Metrics: screenPageViews, activeUsers, screenPageViewsPerUser,
             userEngagementDuration, keyEvents
    """
    client, property_id = get_client_and_property()
    dr = [{"start_date": start_date, "end_date": end_date}]
    if compare_start_date and compare_end_date:
        dr.append({"start_date": compare_start_date, "end_date": compare_end_date})
    return _run_report(
        client,
        property_id,
        date_ranges=dr,
        dimensions=["unifiedPagePathScreen"],
        metrics=[
            "screenPageViews",
            "activeUsers",
            "screenPageViewsPerUser",
            "userEngagementDuration",
            "keyEvents",
        ],
        limit=limit,
    )


# ---------------------------------------------------------------------------
# 4. Page Engagement
# ---------------------------------------------------------------------------

def page_engagement(start_date, end_date, limit=20, compare_start_date=None, compare_end_date=None):
    """Which pages keep people engaged vs. lose them.

    Optionally compare against a second date range.

    Dimensions: unifiedPagePathScreen
    Metrics: screenPageViews, activeUsers, screenPageViewsPerUser,
             userEngagementDuration, keyEvents
    """
    client, property_id = get_client_and_property()
    dr = [{"start_date": start_date, "end_date": end_date}]
    if compare_start_date and compare_end_date:
        dr.append({"start_date": compare_start_date, "end_date": compare_end_date})
    return _run_report(
        client,
        property_id,
        date_ranges=dr,
        dimensions=["unifiedPagePathScreen"],
        metrics=[
            "screenPageViews",
            "activeUsers",
            "screenPageViewsPerUser",
            "userEngagementDuration",
            "keyEvents",
        ],
        limit=limit,
    )


# ---------------------------------------------------------------------------
# 5. Meaningful Actions
# ---------------------------------------------------------------------------

def meaningful_actions(start_date, end_date, limit=20, compare_start_date=None, compare_end_date=None):
    """Whether visitors are completing important actions.

    Optionally compare against a second date range.

    Dimensions: eventName
    Metrics: eventCount, totalUsers, eventCountPerUser
    """
    client, property_id = get_client_and_property()
    dr = [{"start_date": start_date, "end_date": end_date}]
    if compare_start_date and compare_end_date:
        dr.append({"start_date": compare_start_date, "end_date": compare_end_date})
    return _run_report(
        client,
        property_id,
        date_ranges=dr,
        dimensions=["eventName"],
        metrics=["eventCount", "totalUsers", "eventCountPerUser"],
        limit=limit,
    )


# ---------------------------------------------------------------------------
# CLI convenience (for quick testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    funcs = {
        "1": ("Monthly Traffic", monthly_traffic),
        "2": ("Acquisition Channels", acquisition_channels),
        "3": ("Top Traffic Pages", top_traffic_pages),
        "4": ("Page Engagement", page_engagement),
        "5": ("Meaningful Actions", meaningful_actions),
    }

    print("GA4 Report Query")
    print("=" * 40)
    for key, (label, _) in funcs.items():
        print(f"  {key}. {label}")
    print()

    choice = input("Choose report (1-5): ").strip()
    if choice not in funcs:
        print("Invalid choice.")
        sys.exit(1)

    start = input("Start date (YYYY-MM-DD or NdaysAgo): ").strip() or "30daysAgo"
    end = input("End date (YYYY-MM-DD or today): ").strip() or "today"

    compare = input("Compare to another range? (y/n): ").strip().lower() == "y"
    compare_start = None
    compare_end = None
    if compare:
        compare_start = input("Comparison start date: ").strip()
        compare_end = input("Comparison end date: ").strip()

    label, fn = funcs[choice]
    print(f"\nRunning: {label} ({start} to {end})...\n")

    try:
        result = fn(start, end, compare_start_date=compare_start, compare_end_date=compare_end)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        sys.exit(1)
