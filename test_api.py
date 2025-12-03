#!/usr/bin/env python3
"""
Test the ST5 Finale showtimes API to find ways to get all theater data.
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://showtimes-v2.s-prod.pow.io/v2.0/screenings/location"
MOVIE_ID = "09f2b208-6381-4876-b38d-12e9730efe40"

# US geographic center (Kansas)
US_CENTER_LAT = 39.8283
US_CENTER_LON = -98.5795

def make_request(lat, lon, limit=10, offset=0, location_name="US Center"):
    """Make a request to the API with given parameters."""
    today = datetime.now().strftime("%Y-%m-%d")
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    params = {
        "limit": limit,
        "offset": offset,
        "movie_id": MOVIE_ID,
        "deeplink_providers": "base:webedia,fandango,amc,atom,pow|ca:webedia,pow",
        "showtimes_providers": "base:pow|ca:webedia,pow",
        "ticket_providers[ca]": "direct",
        "today": today,
        "local_time": local_time,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "content-type": "application/json",
        "x-requested-lat": str(lat),
        "x-requested-lon": str(lon),
        "x-requested-countries": "CA,US",
        "x-requested-approxpos": location_name,
        "Origin": "https://st5finale.com",
        "Referer": "https://st5finale.com/",
    }

    response = requests.get(BASE_URL, params=params, headers=headers)
    return response.json()

def test_high_limit():
    """Test if we can get all theaters with a high limit from US center."""
    print("=" * 60)
    print("TEST 1: High limit from US geographic center")
    print("=" * 60)

    # Try with very high limit
    for limit in [100, 500, 1000, 5000]:
        print(f"\nTrying limit={limit}...")
        result = make_request(US_CENTER_LAT, US_CENTER_LON, limit=limit)

        if result.get("result") == "ok":
            data = result["response"]["data"]
            more = result["response"]["meta"].get("more", False)
            print(f"  Got {len(data)} theaters, more={more}")

            if data:
                # Show first and last theater distance
                first = data[0]
                last = data[-1]
                print(f"  First: {first['name']} ({first['address']['intl']['city']}, {first['address']['intl']['state']})")
                print(f"  Last: {last['name']} ({last['address']['intl']['city']}, {last['address']['intl']['state']})")

            if not more:
                print(f"\n  SUCCESS! Got all {len(data)} theaters with limit={limit}")
                return data
        else:
            print(f"  Error: {result}")

    return None

def test_without_location():
    """Test if omitting location headers works."""
    print("\n" + "=" * 60)
    print("TEST 2: Try without location headers")
    print("=" * 60)

    today = datetime.now().strftime("%Y-%m-%d")
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    params = {
        "limit": 1000,
        "offset": 0,
        "movie_id": MOVIE_ID,
        "deeplink_providers": "base:webedia,fandango,amc,atom,pow|ca:webedia,pow",
        "showtimes_providers": "base:pow|ca:webedia,pow",
        "ticket_providers[ca]": "direct",
        "today": today,
        "local_time": local_time,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
        "Accept": "*/*",
        "content-type": "application/json",
        "x-requested-countries": "CA,US",
        "Origin": "https://st5finale.com",
    }

    response = requests.get(BASE_URL, params=params, headers=headers)
    result = response.json()

    if result.get("result") == "ok":
        data = result["response"]["data"]
        more = result["response"]["meta"].get("more", False)
        print(f"Got {len(data)} theaters, more={more}")
        return data
    else:
        print(f"Error: {result}")

    return None

def test_pagination_from_center():
    """Paginate through all results from US center."""
    print("\n" + "=" * 60)
    print("TEST 3: Paginate through all results from US center")
    print("=" * 60)

    all_theaters = []
    seen_ids = set()
    offset = 0
    limit = 100

    while True:
        print(f"\nFetching offset={offset}...")
        result = make_request(US_CENTER_LAT, US_CENTER_LON, limit=limit, offset=offset)

        if result.get("result") != "ok":
            print(f"Error: {result}")
            break

        data = result["response"]["data"]
        more = result["response"]["meta"].get("more", False)

        new_count = 0
        for theater in data:
            if theater["id"] not in seen_ids:
                seen_ids.add(theater["id"])
                all_theaters.append(theater)
                new_count += 1

        print(f"  Got {len(data)} theaters ({new_count} new), total: {len(all_theaters)}, more={more}")

        if not more or len(data) == 0:
            break

        offset += limit

        # Safety limit
        if offset > 10000:
            print("Safety limit reached")
            break

    return all_theaters

def test_multiple_locations():
    """Test from multiple major metro areas to understand coverage."""
    print("\n" + "=" * 60)
    print("TEST 4: Multiple locations with high limits")
    print("=" * 60)

    # Major population centers across US
    locations = [
        (40.7128, -74.0060, "New York, NY"),
        (34.0522, -118.2437, "Los Angeles, CA"),
        (41.8781, -87.6298, "Chicago, IL"),
        (29.7604, -95.3698, "Houston, TX"),
        (33.4484, -112.0740, "Phoenix, AZ"),
        (47.6062, -122.3321, "Seattle, WA"),
        (25.7617, -80.1918, "Miami, FL"),
        (39.7392, -104.9903, "Denver, CO"),
        (42.3601, -71.0589, "Boston, MA"),
        (33.7490, -84.3880, "Atlanta, GA"),
    ]

    all_theaters = {}
    total_unique = 0

    for lat, lon, name in locations:
        print(f"\n{name}:")
        result = make_request(lat, lon, limit=500, location_name=name)

        if result.get("result") == "ok":
            data = result["response"]["data"]
            more = result["response"]["meta"].get("more", False)

            new_count = 0
            for t in data:
                if t["id"] not in all_theaters:
                    all_theaters[t["id"]] = t
                    new_count += 1

            print(f"  Got {len(data)} theaters ({new_count} new unique), more={more}")

            if data:
                # Check the farthest theater
                last = data[-1]
                print(f"  Farthest: {last['name']} ({last['address']['intl']['city']}, {last['address']['intl']['state']})")
        else:
            print(f"  Error: {result}")

        import time
        time.sleep(0.5)

    print(f"\n\nTotal unique theaters: {len(all_theaters)}")
    return all_theaters

def paginate_from_location(lat, lon, name):
    """Fully paginate from a single location."""
    all_theaters = []
    seen_ids = set()
    offset = 0
    limit = 100

    while True:
        result = make_request(lat, lon, limit=limit, offset=offset, location_name=name)

        if result.get("result") != "ok":
            break

        data = result["response"]["data"]
        more = result["response"]["meta"].get("more", False)

        for theater in data:
            if theater["id"] not in seen_ids:
                seen_ids.add(theater["id"])
                all_theaters.append(theater)

        if not more or len(data) == 0:
            break

        offset += limit

        if offset > 20000:
            break

    return all_theaters

def test_full_pagination_from_ny():
    """Test full pagination from New York."""
    print("\n" + "=" * 60)
    print("TEST 5: Full pagination from New York")
    print("=" * 60)

    theaters = paginate_from_location(40.7128, -74.0060, "New York")
    print(f"Total theaters from NY pagination: {len(theaters)}")

    if theaters:
        # Group by state
        by_state = {}
        for t in theaters:
            state = t["address"]["intl"].get("state", "Unknown")
            country = t["address"]["intl"].get("country", "Unknown")
            key = f"{state}, {country}" if country != "US" else state
            by_state.setdefault(key, []).append(t)

        print("\nBy state:")
        for state in sorted(by_state.keys()):
            print(f"  {state}: {len(by_state[state])} theaters")

    return theaters

if __name__ == "__main__":
    import time

    # Test from multiple locations first
    theaters_dict = test_multiple_locations()

    print("\n")

    # Try full pagination from NY
    ny_theaters = test_full_pagination_from_ny()

    # Compare
    print(f"\n\nSUMMARY:")
    print(f"  Multi-location sampling: {len(theaters_dict)} unique theaters")
    print(f"  Full pagination from NY: {len(ny_theaters)} theaters")
