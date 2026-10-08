"""Live lodging search tool querying real-time web results."""

from typing import Any
from urllib.parse import quote_plus
from ddgs import DDGS


def search_live_lodgings(
    destination: str,
    area_or_requirements: str = "",
    max_price_per_night: float | None = None,
    min_rating: float | None = None,
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """Search for live, real-time lodging options and hotels on the web.

    Use this tool when looking up real hotels, boutique stays, ryokans, or lodges in any city,
    including current booking links, reviews, and neighborhood descriptions.

    Args:
        destination: City or destination to search (e.g. 'Tokyo', 'Kyoto', 'Paris').
        area_or_requirements: Specific neighborhood, district, or requirements (e.g., 'Shinjuku near subway', 'Montmartre with view').
        max_price_per_night: Optional budget ceiling per night in USD.
        min_rating: Optional desired minimum rating (e.g. 4.0 or 4.5).
        max_results: Maximum search results to retrieve (default 5).

    Returns:
        A list of real lodging search results with titles, descriptions, booking website URLs, and Google Maps search links.
    """
    query_parts = ["hotels lodging accommodations", destination]
    if area_or_requirements:
        query_parts.append(area_or_requirements)
    if max_price_per_night is not None:
        query_parts.append(f"under ${int(max_price_per_night)}")
    if min_rating is not None:
        query_parts.append(f"{min_rating}+ star rating reviews")

    query = " ".join(query_parts)

    try:
        raw_results = list(DDGS().text(query, max_results=max_results))
        formatted_results = []

        for r in raw_results:
            title = r.get("title", "")
            href = r.get("href", "")
            snippet = r.get("body", "")

            # Generate convenient Google Maps search link for the location/title
            clean_search_term = f"{title.split(' - ')[0]} {destination}"
            maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(clean_search_term)}"

            formatted_results.append({
                "title": title,
                "website_url": href,
                "google_maps_url": maps_url,
                "summary": snippet,
                "destination": destination,
            })

        return formatted_results

    except Exception as e:
        return [{
            "status": "error",
            "message": f"Live lodging search failed: {str(e)}",
            "destination": destination,
        }]
