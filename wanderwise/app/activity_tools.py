"""Tool for discovering destination activities, attractions, and sights using public APIs."""

from typing import Any
from urllib.parse import quote_plus
from ddgs import DDGS


def search_destination_activities(
    destination: str,
    experience_type: str = "",
    vibe: str = "",
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """Search for real attractions, sights, food spots, and daily activities for a travel destination.

    Args:
        destination: City or region (e.g. 'Tokyo', 'Paris', 'San Francisco').
        experience_type: Desired experiences (e.g. 'temples & historical sights', 'hidden culinary spots', 'art museums').
        vibe: Pace or style (e.g. 'relaxed cultural', 'fast-paced adventure', 'family friendly').
        max_results: Maximum number of activity recommendations to return (default 5).

    Returns:
        List of activities with title, description, official/travel guide URL, and ready-to-click Google Maps search link.
    """
    query_parts = ["top attractions things to do sightseeing in", destination]
    if experience_type:
        query_parts.append(experience_type)
    if vibe:
        query_parts.append(vibe)

    query = " ".join(query_parts)

    try:
        raw_results = list(DDGS().text(query, max_results=max_results))
        activities = []

        for r in raw_results:
            title = r.get("title", "")
            href = r.get("href", "")
            snippet = r.get("body", "")

            # Generate Google Maps search URL for the activity / venue
            clean_name = title.split(" - ")[0].split(" | ")[0]
            maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(f'{clean_name}, {destination}')}"

            activities.append({
                "activity_name": clean_name,
                "full_title": title,
                "description": snippet,
                "website_url": href,
                "google_maps_url": maps_url,
                "destination": destination,
            })

        return activities

    except Exception as e:
        return [{
            "status": "error",
            "message": f"Failed to retrieve activities: {str(e)}",
            "destination": destination,
        }]
