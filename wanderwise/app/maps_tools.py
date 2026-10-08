"""Google Maps links and directions tool for WanderWise."""

from urllib.parse import quote_plus
from typing import Any


def generate_google_maps_link(
    place_name: str,
    city_or_destination: str = "",
    starting_point: str | None = None,
) -> dict[str, Any]:
    """Generate official Google Maps search or directions links for an activity, venue, or hotel.

    Args:
        place_name: Name of the attraction, hotel, restaurant, or landmark (e.g. 'Senso-ji Temple', 'Shinjuku Gyoen National Garden').
        city_or_destination: City or region to ensure accurate pin location (e.g. 'Tokyo, Japan').
        starting_point: Optional origin location if step-by-step navigation directions are requested (e.g. 'Granbell Hotel Shinjuku').

    Returns:
        Dictionary with place search link, directions navigation link, and embed-ready link.
    """
    full_place_query = f"{place_name}, {city_or_destination}".strip(", ")
    encoded_query = quote_plus(full_place_query)

    search_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

    directions_url = None
    if starting_point:
        origin_encoded = quote_plus(f"{starting_point}, {city_or_destination}".strip(", "))
        directions_url = (
            f"https://www.google.com/maps/dir/?api=1&origin={origin_encoded}&destination={encoded_query}&travelmode=transit"
        )

    return {
        "place_name": place_name,
        "destination": city_or_destination,
        "maps_search_url": search_url,
        "directions_url": directions_url,
        "google_maps_link": directions_url or search_url,
    }
