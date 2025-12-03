#!/usr/bin/env python3
"""
Comprehensive scraper for ST5 Finale theater locations.
Uses a geographic grid to ensure complete coverage of US and Canada.
"""

import requests
import json
import time
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
import sys

BASE_URL = "https://showtimes-v2.s-prod.pow.io/v2.0/screenings/location"
MOVIE_ID = "09f2b208-6381-4876-b38d-12e9730efe40"

# Geographic grid points covering US and Canada
# Optimized coverage - 120 points
GRID_POINTS = [
    # West Coast
    (47.6062, -122.3321, "Seattle"),
    (45.5152, -122.6784, "Portland"),
    (44.0521, -123.0868, "Eugene"),
    (38.5816, -121.4944, "Sacramento"),
    (37.7749, -122.4194, "San Francisco"),
    (37.3382, -121.8863, "San Jose"),
    (36.7783, -119.4179, "Fresno"),
    (35.3733, -119.0187, "Bakersfield"),
    (34.0522, -118.2437, "Los Angeles"),
    (33.6846, -117.8265, "Irvine"),
    (32.7157, -117.1611, "San Diego"),

    # Mountain West
    (47.6588, -117.4260, "Spokane"),
    (46.8787, -113.9966, "Missoula"),
    (45.7833, -108.5007, "Billings MT"),
    (43.6187, -116.2146, "Boise"),
    (40.7608, -111.8910, "Salt Lake City"),
    (39.5296, -119.8138, "Reno"),
    (36.1699, -115.1398, "Las Vegas"),
    (33.4484, -112.0740, "Phoenix"),
    (32.2226, -110.9747, "Tucson"),
    (39.7392, -104.9903, "Denver"),
    (38.8339, -104.8214, "Colorado Springs"),
    (35.0844, -106.6504, "Albuquerque"),

    # Texas
    (35.2220, -101.8313, "Amarillo"),
    (31.7619, -106.4850, "El Paso"),
    (32.7767, -96.7970, "Dallas"),
    (32.7555, -97.3308, "Fort Worth"),
    (31.5493, -97.1467, "Waco"),
    (30.2672, -97.7431, "Austin"),
    (29.7604, -95.3698, "Houston"),
    (29.4241, -98.4936, "San Antonio"),
    (27.8006, -97.3964, "Corpus Christi"),
    (33.4152, -94.0428, "Texarkana"),

    # Midwest
    (46.8772, -96.7898, "Fargo"),
    (44.9778, -93.2650, "Minneapolis"),
    (43.5460, -96.7313, "Sioux Falls"),
    (41.2565, -95.9345, "Omaha"),
    (37.6872, -97.3301, "Wichita"),
    (39.0997, -94.5786, "Kansas City"),
    (38.6270, -90.1994, "St Louis"),
    (38.2527, -85.7585, "Louisville"),
    (39.7684, -86.1581, "Indianapolis"),
    (41.5868, -93.6250, "Des Moines"),
    (43.0731, -89.4012, "Madison"),
    (43.0389, -87.9065, "Milwaukee"),
    (41.8781, -87.6298, "Chicago"),
    (40.6936, -89.5890, "Peoria"),
    (42.3314, -83.0458, "Detroit"),
    (42.9634, -85.6681, "Grand Rapids"),
    (41.4993, -81.6944, "Cleveland"),
    (39.9612, -82.9988, "Columbus OH"),
    (39.1031, -84.5120, "Cincinnati"),
    (41.6639, -83.5552, "Toledo"),

    # South
    (35.4676, -97.5164, "Oklahoma City"),
    (36.1540, -95.9928, "Tulsa"),
    (34.7465, -92.2896, "Little Rock"),
    (35.1495, -90.0490, "Memphis"),
    (36.1627, -86.7816, "Nashville"),
    (35.9606, -83.9207, "Knoxville"),
    (33.5207, -86.8025, "Birmingham"),
    (32.3792, -86.3077, "Montgomery"),
    (30.6954, -88.0399, "Mobile"),
    (32.2988, -90.1848, "Jackson MS"),
    (30.4515, -91.1871, "Baton Rouge"),
    (29.9511, -90.0715, "New Orleans"),

    # Southeast
    (33.7490, -84.3880, "Atlanta"),
    (32.0809, -81.0912, "Savannah"),
    (30.4383, -84.2807, "Tallahassee"),
    (30.3322, -81.6557, "Jacksonville"),
    (28.5383, -81.3792, "Orlando"),
    (27.9506, -82.4572, "Tampa"),
    (26.6406, -81.8723, "Fort Myers"),
    (26.1224, -80.1373, "Fort Lauderdale"),
    (25.7617, -80.1918, "Miami"),
    (26.7153, -80.0534, "West Palm Beach"),

    # Carolinas & Virginia
    (35.2271, -80.8431, "Charlotte"),
    (35.7796, -78.6382, "Raleigh"),
    (35.5951, -82.5515, "Asheville"),
    (34.0007, -81.0348, "Columbia SC"),
    (32.7765, -79.9311, "Charleston SC"),
    (37.5407, -77.4360, "Richmond"),
    (36.8508, -75.9779, "Virginia Beach"),

    # Northeast
    (38.9072, -77.0369, "Washington DC"),
    (39.2904, -76.6122, "Baltimore"),
    (39.9526, -75.1652, "Philadelphia"),
    (40.7357, -74.1724, "Newark NJ"),
    (40.7128, -74.0060, "New York"),
    (41.3083, -72.9279, "New Haven"),
    (41.7658, -72.6734, "Hartford"),
    (41.8240, -71.4128, "Providence"),
    (42.3601, -71.0589, "Boston"),
    (43.6591, -70.2568, "Portland ME"),
    (43.0096, -71.4545, "Manchester NH"),
    (42.6526, -73.7562, "Albany"),
    (43.0481, -76.1474, "Syracuse"),
    (43.1610, -77.6109, "Rochester NY"),
    (42.8864, -78.8784, "Buffalo"),
    (40.4406, -79.9959, "Pittsburgh"),
    (40.6084, -75.4902, "Allentown"),
    (42.1292, -80.0851, "Erie PA"),

    # Canada
    (49.2827, -123.1207, "Vancouver BC"),
    (51.0447, -114.0719, "Calgary AB"),
    (53.5461, -113.4938, "Edmonton AB"),
    (49.8951, -97.1384, "Winnipeg MB"),
    (43.6532, -79.3832, "Toronto ON"),
    (43.2557, -79.8711, "Hamilton ON"),
    (42.9849, -81.2453, "London ON"),
    (45.4215, -75.6972, "Ottawa ON"),
    (45.5017, -73.5673, "Montreal QC"),
    (46.8139, -71.2080, "Quebec City QC"),
    (46.0878, -64.7782, "Moncton NB"),
    (44.6488, -63.5752, "Halifax NS"),
]


def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance in miles between two points."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 3956  # Earth radius in miles


def make_request(lat, lon, limit=20, offset=0, location_name=""):
    """Make a request to the API."""
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

    response = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
    return response.json()


def paginate_location(lat, lon, name):
    """Get all theaters from a single location with pagination."""
    theaters = []
    seen_ids = set()
    offset = 0

    while True:
        result = make_request(lat, lon, limit=20, offset=offset, location_name=name)

        if result.get("result") != "ok":
            break

        data = result["response"]["data"]
        more = result["response"]["meta"].get("more", False)

        for theater in data:
            if theater["id"] not in seen_ids:
                seen_ids.add(theater["id"])
                theaters.append(theater)

        if not more or len(data) == 0:
            break

        offset += 20
        time.sleep(0.1)  # Rate limiting

        if offset > 500:  # Safety limit
            break

    return theaters


def scrape_all():
    """Scrape all theaters using geographic grid."""
    all_theaters = {}
    total_points = len(GRID_POINTS)

    print(f"Scraping from {total_points} geographic points...")
    print("-" * 60)

    for i, (lat, lon, name) in enumerate(GRID_POINTS):
        sys.stdout.write(f"\r[{i+1}/{total_points}] {name}...")
        sys.stdout.flush()

        try:
            theaters = paginate_location(lat, lon, name)

            new_count = 0
            for t in theaters:
                if t["id"] not in all_theaters:
                    all_theaters[t["id"]] = t
                    new_count += 1

            sys.stdout.write(f"\r[{i+1}/{total_points}] {name}: {len(theaters)} theaters ({new_count} new), total: {len(all_theaters)}\n")
        except Exception as e:
            sys.stdout.write(f"\r[{i+1}/{total_points}] {name}: ERROR - {e}\n")

        time.sleep(0.3)  # Rate limiting between locations

    return list(all_theaters.values())


def format_theater(t):
    """Format a theater for clean output."""
    addr = t["address"]["intl"]

    # Convert screeningsDates timestamps to dates (UTC)
    screening_dates = []
    for ts in t.get("screeningsDates", []):
        try:
            # Convert milliseconds to datetime (UTC)
            dt = datetime.utcfromtimestamp(ts / 1000)
            screening_dates.append(dt.strftime("%Y-%m-%d"))
        except:
            pass

    # Get ticket link
    ticket_link = ""
    screenings = t.get("screenings", [])
    if screenings:
        link_obj = screenings[0].get("link", {})
        if isinstance(link_obj, dict):
            ticket_link = link_obj.get("direct", "")
        elif isinstance(link_obj, str):
            ticket_link = link_obj
    if not ticket_link:
        ticket_link = t.get("url", "")

    return {
        "id": t["id"],
        "name": t["name"],
        "chain_id": t.get("chainId"),
        "url": t.get("url"),
        "ticket_link": ticket_link,
        "lat": t["lat"],
        "lon": t["lon"],
        "address": {
            "street": addr.get("street", ""),
            "city": addr.get("city", ""),
            "state": addr.get("state", ""),
            "postcode": addr.get("postcode", ""),
            "country": addr.get("country", ""),
        },
        "screening_dates": screening_dates if screening_dates else ["2025-12-31", "2026-01-01"],
    }


def main():
    print("=" * 60)
    print("ST5 FINALE THEATER SCRAPER")
    print("=" * 60)
    print()

    theaters = scrape_all()

    print()
    print("=" * 60)
    print(f"SCRAPING COMPLETE: {len(theaters)} unique theaters found")
    print("=" * 60)

    # Format and sort theaters
    formatted = [format_theater(t) for t in theaters]
    formatted.sort(key=lambda x: (x["address"]["country"] or "", x["address"]["state"] or "", x["address"]["city"] or "", x["name"] or ""))

    # Group by state/province
    by_region = {}
    for t in formatted:
        country = t["address"]["country"] or "Unknown"
        state = t["address"]["state"] or "Unknown"
        region = f"{state}, {country}" if country != "US" else state
        by_region.setdefault(region, []).append(t)

    print("\nBy Region:")
    for region in sorted(by_region.keys()):
        print(f"  {region}: {len(by_region[region])} theaters")

    # Count by country
    us_count = sum(1 for t in formatted if t["address"]["country"] == "US")
    ca_count = sum(1 for t in formatted if t["address"]["country"] == "CA")

    # Save to JSON
    output = {
        "scraped_at": datetime.now().isoformat(),
        "movie_id": MOVIE_ID,
        "movie_title": "Stranger Things 5: The Finale",
        "screening_dates": ["2025-12-31", "2026-01-01"],
        "total_theaters": len(formatted),
        "us_theaters": us_count,
        "ca_theaters": ca_count,
        "by_region": {r: len(ts) for r, ts in sorted(by_region.items())},
        "theaters": formatted,
    }

    output_file = "st5_finale_theaters.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to {output_file}")

    # Create comprehensive sorted text list
    sorted_file = "st5_finale_theaters_sorted.txt"
    with open(sorted_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("STRANGER THINGS 5: THE FINALE - COMPLETE THEATER LIST\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Theaters: {len(formatted)}\n")
        f.write(f"  United States: {us_count}\n")
        f.write(f"  Canada: {ca_count}\n\n")
        f.write("Screening Dates: December 31, 2025 & January 1, 2026\n")
        f.write("Note: Specific showtimes available at theater ticket links\n\n")
        f.write("-" * 80 + "\n")
        f.write("TOP STATES/PROVINCES BY THEATER COUNT:\n")
        f.write("-" * 80 + "\n")

        # Sort regions by count
        sorted_regions = sorted(by_region.items(), key=lambda x: -len(x[1]))
        for region, ts in sorted_regions[:15]:
            f.write(f"  {region}: {len(ts)} theaters\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("THEATERS BY CITY (Alphabetical)\n")
        f.write("=" * 80 + "\n")

        current_letter = ""
        for t in formatted:
            city = t["address"]["city"] or "Unknown"
            state = t["address"]["state"] or ""
            country = t["address"]["country"] or ""
            name = t["name"]

            # Format dates
            dates = t.get("screening_dates", ["2025-12-31", "2026-01-01"])
            dates_str = ", ".join(dates) if dates else "Dec 31, 2025 & Jan 1, 2026"

            # Get ticket link
            link = t.get("ticket_link", "") or t.get("url", "")

            # Add letter header
            first_letter = city[0].upper() if city else "?"
            if first_letter != current_letter:
                current_letter = first_letter
                f.write(f"\n--- {current_letter} ---\n\n")

            # Format location
            if country == "US":
                location = f"{city}, {state}" if state else city
            elif country == "CA":
                location = f"{city}, {state}, Canada" if state else f"{city}, Canada"
            else:
                location = f"{city}, {state}, {country}" if state else f"{city}, {country}"

            f.write(f"{location}\n")
            f.write(f"  {name}\n")
            f.write(f"  Dates: {dates_str}\n")
            f.write(f"  Tickets: {link}\n")
            f.write("\n")

    print(f"Saved sorted list to {sorted_file}")


if __name__ == "__main__":
    main()
