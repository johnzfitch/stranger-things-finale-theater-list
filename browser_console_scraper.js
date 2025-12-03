/**
 * ST5 Finale Theater Scraper - Browser Console Version
 *
 * Run this in your browser console while on st5finale.com
 * It will fetch all theaters by querying from multiple geographic points.
 */

(async function scrapeAllTheaters() {
    const MOVIE_ID = "09f2b208-6381-4876-b38d-12e9730efe40";
    const BASE_URL = "https://showtimes-v2.s-prod.pow.io/v2.0/screenings/location";

    // Key geographic points (subset for browser - full version in Python)
    const LOCATIONS = [
        [47.6062, -122.3321, "Seattle"],
        [45.5152, -122.6784, "Portland"],
        [37.7749, -122.4194, "San Francisco"],
        [34.0522, -118.2437, "Los Angeles"],
        [33.4484, -112.0740, "Phoenix"],
        [32.7157, -117.1611, "San Diego"],
        [40.7608, -111.8910, "Salt Lake City"],
        [39.7392, -104.9903, "Denver"],
        [36.1699, -115.1398, "Las Vegas"],
        [32.7767, -96.7970, "Dallas"],
        [29.7604, -95.3698, "Houston"],
        [29.4241, -98.4936, "San Antonio"],
        [30.2672, -97.7431, "Austin"],
        [44.9778, -93.2650, "Minneapolis"],
        [41.8781, -87.6298, "Chicago"],
        [42.3314, -83.0458, "Detroit"],
        [41.4993, -81.6944, "Cleveland"],
        [39.7684, -86.1581, "Indianapolis"],
        [38.6270, -90.1994, "St Louis"],
        [33.7490, -84.3880, "Atlanta"],
        [35.2271, -80.8431, "Charlotte"],
        [36.1627, -86.7816, "Nashville"],
        [30.3322, -81.6557, "Jacksonville"],
        [27.9506, -82.4572, "Tampa"],
        [25.7617, -80.1918, "Miami"],
        [29.9511, -90.0715, "New Orleans"],
        [40.7128, -74.0060, "New York"],
        [39.9526, -75.1652, "Philadelphia"],
        [42.3601, -71.0589, "Boston"],
        [38.9072, -77.0369, "Washington DC"],
        [40.4406, -79.9959, "Pittsburgh"],
        [42.8864, -78.8784, "Buffalo"],
        [49.2827, -123.1207, "Vancouver BC"],
        [51.0447, -114.0719, "Calgary AB"],
        [43.6532, -79.3832, "Toronto ON"],
        [45.5017, -73.5673, "Montreal QC"],
    ];

    async function fetchTheaters(lat, lon, name) {
        const today = new Date().toISOString().split('T')[0];
        const localTime = new Date().toISOString().replace('T', ' ').substring(0, 19);

        const params = new URLSearchParams({
            limit: 100,
            offset: 0,
            movie_id: MOVIE_ID,
            deeplink_providers: "base:webedia,fandango,amc,atom,pow|ca:webedia,pow",
            showtimes_providers: "base:pow|ca:webedia,pow",
            "ticket_providers[ca]": "direct",
            today: today,
            local_time: localTime,
        });

        const response = await fetch(`${BASE_URL}?${params}`, {
            headers: {
                "content-type": "application/json",
                "x-requested-lat": lat.toString(),
                "x-requested-lon": lon.toString(),
                "x-requested-countries": "CA,US",
                "x-requested-approxpos": name,
            }
        });

        const data = await response.json();
        return data.response?.data || [];
    }

    const allTheaters = new Map();

    console.log(`%cST5 Finale Theater Scraper`, 'font-size: 16px; font-weight: bold; color: #E50914');
    console.log(`Scraping from ${LOCATIONS.length} locations...`);

    for (const [lat, lon, name] of LOCATIONS) {
        try {
            const theaters = await fetchTheaters(lat, lon, name);
            let newCount = 0;

            for (const theater of theaters) {
                if (!allTheaters.has(theater.id)) {
                    allTheaters.set(theater.id, {
                        id: theater.id,
                        name: theater.name,
                        lat: theater.lat,
                        lon: theater.lon,
                        city: theater.address?.intl?.city,
                        state: theater.address?.intl?.state,
                        country: theater.address?.intl?.country,
                        street: theater.address?.intl?.street,
                        postcode: theater.address?.intl?.postcode,
                        url: theater.url,
                        ticketLink: theater.screenings?.[0]?.link?.direct,
                        screeningDate: theater.screenings?.[0]?.date,
                    });
                    newCount++;
                }
            }

            console.log(`${name}: ${theaters.length} theaters (${newCount} new), total: ${allTheaters.size}`);

            // Rate limiting
            await new Promise(resolve => setTimeout(resolve, 300));
        } catch (error) {
            console.error(`Error fetching ${name}:`, error);
        }
    }

    const theatersArray = Array.from(allTheaters.values());
    theatersArray.sort((a, b) => {
        const countryCompare = (a.country || '').localeCompare(b.country || '');
        if (countryCompare !== 0) return countryCompare;
        const stateCompare = (a.state || '').localeCompare(b.state || '');
        if (stateCompare !== 0) return stateCompare;
        return (a.city || '').localeCompare(b.city || '');
    });

    // Output results
    console.log(`%c\nSCRAPING COMPLETE: ${theatersArray.length} unique theaters found!`, 'font-size: 14px; font-weight: bold; color: #00FF00');

    // Group by state
    const byState = {};
    theatersArray.forEach(t => {
        const key = t.country === 'US' ? t.state : `${t.state || 'Unknown'}, ${t.country}`;
        if (!byState[key]) byState[key] = [];
        byState[key].push(t);
    });

    console.log('\nBy State/Province:');
    Object.keys(byState).sort().forEach(state => {
        console.log(`  ${state}: ${byState[state].length} theaters`);
    });

    // Store in window for easy access
    window.st5theaters = theatersArray;
    window.st5theatersByState = byState;

    console.log('\n%cData stored in window.st5theaters and window.st5theatersByState', 'color: #00BFFF');
    console.log('To copy as JSON: copy(JSON.stringify(window.st5theaters, null, 2))');

    // Offer download using safe DOM methods
    const blob = new Blob([JSON.stringify({
        scraped_at: new Date().toISOString(),
        movie_title: "Stranger Things 5: The Finale",
        total_theaters: theatersArray.length,
        theaters: theatersArray
    }, null, 2)], { type: 'application/json' });

    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(blob);
    downloadLink.download = 'st5_finale_theaters.json';
    downloadLink.textContent = 'Download JSON';
    downloadLink.style.cssText = 'display: block; background: #E50914; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px 0; text-align: center; font-weight: bold;';

    // Build UI using safe DOM methods
    const container = document.createElement('div');
    container.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 99999; background: #141414; padding: 20px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.5);';

    const innerDiv = document.createElement('div');
    innerDiv.style.cssText = 'color: white; font-family: sans-serif;';

    const heading = document.createElement('h3');
    heading.style.cssText = 'margin: 0 0 10px; color: #E50914;';
    heading.textContent = 'Scraping Complete!';

    const paragraph = document.createElement('p');
    paragraph.textContent = `${theatersArray.length} theaters found`;

    innerDiv.appendChild(heading);
    innerDiv.appendChild(paragraph);
    container.appendChild(innerDiv);
    container.appendChild(downloadLink);
    document.body.appendChild(container);

    return theatersArray;
})();
