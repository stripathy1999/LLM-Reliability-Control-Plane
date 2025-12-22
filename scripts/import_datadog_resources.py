#!/usr/bin/env python3
"""
Helper script to import Datadog resources (monitors, dashboard, SLO) via API.

Usage:
    python scripts/import_datadog_resources.py

Requires environment variables:
    - LRCP_DATADOG_API_KEY: Datadog API key
    - DD_APP_KEY: Datadog Application key
    - DD_SITE: Datadog site (default: datadoghq.com)
"""

import json
import os
import sys
from pathlib import Path

import httpx


def get_env(key: str, default: str | None = None) -> str:
    """Get environment variable or raise error if missing."""
    value = os.getenv(key, default)
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


def import_monitors(api_key: str, app_key: str, site: str) -> None:
    """Import monitors from datadog/monitors.json."""
    monitors_path = Path(__file__).parent.parent / "datadog" / "monitors.json"
    with open(monitors_path) as f:
        data = json.load(f)

    base_url = f"https://api.{site}/api/v1"
    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": app_key,
        "Content-Type": "application/json",
    }

    print(f"Importing {len(data['monitors'])} monitors...")
    for monitor in data["monitors"]:
        # Remove incident_config (not part of Datadog API schema)
        monitor_payload = {k: v for k, v in monitor.items() if k != "incident_config"}

        try:
            response = httpx.post(
                f"{base_url}/monitor",
                headers=headers,
                json=monitor_payload,
                timeout=10.0,
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Created monitor: {monitor['name']} (ID: {result.get('id')})")
        except httpx.HTTPStatusError as e:
            print(f"✗ Failed to create monitor {monitor['name']}: {e.response.text}")
        except Exception as e:
            print(f"✗ Error creating monitor {monitor['name']}: {e}")


def import_dashboard(api_key: str, app_key: str, site: str) -> None:
    """Import dashboard from datadog/dashboard.json."""
    dashboard_path = Path(__file__).parent.parent / "datadog" / "dashboard.json"
    with open(dashboard_path) as f:
        dashboard = json.load(f)

    base_url = f"https://api.{site}/api/v1"
    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": app_key,
        "Content-Type": "application/json",
    }

    print("Importing dashboard...")
    try:
        response = httpx.post(
            f"{base_url}/dashboard",
            headers=headers,
            json=dashboard,
            timeout=10.0,
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ Created dashboard: {dashboard['title']} (ID: {result.get('dashboard', {}).get('id')})")
    except httpx.HTTPStatusError as e:
        print(f"✗ Failed to create dashboard: {e.response.text}")
    except Exception as e:
        print(f"✗ Error creating dashboard: {e}")


def import_slo(api_key: str, app_key: str, site: str) -> None:
    """Import SLO from datadog/slo.json."""
    slo_path = Path(__file__).parent.parent / "datadog" / "slo.json"
    with open(slo_path) as f:
        slo = json.load(f)

    base_url = f"https://api.{site}/api/v1"
    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": app_key,
        "Content-Type": "application/json",
    }

    print("Importing SLO...")
    try:
        response = httpx.post(
            f"{base_url}/slo",
            headers=headers,
            json=slo,
            timeout=10.0,
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ Created SLO: {slo['name']} (ID: {result.get('data', {}).get('id')})")
    except httpx.HTTPStatusError as e:
        print(f"✗ Failed to create SLO: {e.response.text}")
    except Exception as e:
        print(f"✗ Error creating SLO: {e}")


def main() -> None:
    """Main entry point."""
    try:
        api_key = get_env("LRCP_DATADOG_API_KEY")
        app_key = get_env("DD_APP_KEY")
        site = os.getenv("DD_SITE", "datadoghq.com")
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set the following environment variables:")
        print("  - LRCP_DATADOG_API_KEY")
        print("  - DD_APP_KEY")
        print("  - DD_SITE (optional, defaults to datadoghq.com)")
        sys.exit(1)

    print("=" * 60)
    print("Datadog Resource Import Script")
    print("=" * 60)
    print()

    import_monitors(api_key, app_key, site)
    print()
    import_dashboard(api_key, app_key, site)
    print()
    import_slo(api_key, app_key, site)
    print()
    print("=" * 60)
    print("Import complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Configure incident rules in Datadog UI (Incidents → Settings → Rules)")
    print("2. Verify monitors are evaluating correctly")
    print("3. Test incident creation by triggering a monitor")


if __name__ == "__main__":
    main()

