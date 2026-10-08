"""Tools for finding local trending events and computing trip budget with overage alerts."""

from typing import Any
from urllib.parse import quote_plus
from ddgs import DDGS


def search_local_events(
    destination: str,
    travel_period: str = "",
    interest_or_vibe: str = "",
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """Search for live trending events, festivals, concerts, and cultural happenings during a trip.

    Args:
        destination: Destination city or region (e.g. 'Tokyo', 'Paris').
        travel_period: Travel dates or month (e.g. 'October 2026', 'Nov 1 - Nov 6').
        interest_or_vibe: Specific interests (e.g., 'art exhibition', 'music festival', 'food market', 'anime').
        max_results: Maximum events to return (default 5).

    Returns:
        List of trending events with title, date/time info, event description, website URL, and Google Maps search link.
    """
    query_parts = ["events festivals happening in", destination]
    if travel_period:
        query_parts.append(travel_period)
    if interest_or_vibe:
        query_parts.append(interest_or_vibe)

    query = " ".join(query_parts)

    try:
        raw_results = list(DDGS().text(query, max_results=max_results))
        events = []

        for r in raw_results:
            title = r.get("title", "")
            href = r.get("href", "")
            snippet = r.get("body", "")

            # Generate Google Maps link for the venue/event location
            clean_venue = f"{title.split(' - ')[0]} {destination}"
            maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(clean_venue)}"

            events.append({
                "event_title": title,
                "description": snippet,
                "website_url": href,
                "google_maps_url": maps_url,
                "destination": destination,
            })

        return events

    except Exception as e:
        return [{
            "status": "error",
            "message": f"Failed to fetch live events: {str(e)}",
            "destination": destination,
        }]


def calculate_trip_budget(
    total_budget: float,
    num_nights: int,
    lodging_price_per_night: float,
    party_size: int = 1,
    estimated_daily_expenses_per_person: float = 80.0,
    currency_symbol: str = "$",
) -> dict[str, Any]:
    """Calculate the complete trip financial breakdown and flag budget overages with warning indicators.

    Args:
        total_budget: The traveler's total budget cap for the trip.
        num_nights: Number of nights staying.
        lodging_price_per_night: Nightly cost for lodging / room.
        party_size: Number of people in the travel group (default 1).
        estimated_daily_expenses_per_person: Estimated cost per person/day for food, transit, & activities (default $80).
        currency_symbol: Currency symbol for display (default '$').

    Returns:
        Dictionary containing itemized costs, per-person breakdown, overage status, and formatted warning banner.
    """
    # Lodging total for the group
    total_lodging_cost = round(lodging_price_per_night * num_nights, 2)

    # Number of trip days is typically num_nights + 1 or at least num_nights
    trip_days = max(num_nights, 1)
    total_daily_expenses = round(estimated_daily_expenses_per_person * trip_days * party_size, 2)

    total_estimated_trip_cost = round(total_lodging_cost + total_daily_expenses, 2)
    difference = round(total_budget - total_estimated_trip_cost, 2)

    cost_per_person = round(total_estimated_trip_cost / party_size, 2) if party_size > 0 else total_estimated_trip_cost

    is_over_budget = difference < 0
    overage_amount = abs(difference) if is_over_budget else 0.0

    if is_over_budget:
        warning_indicator = f"🚨 RED ALERT: OVER BUDGET BY {currency_symbol}{overage_amount:.2f} (Total: {currency_symbol}{total_estimated_trip_cost:.2f} vs Budget: {currency_symbol}{total_budget:.2f})"
        budget_status = "OVER_BUDGET"
    else:
        warning_indicator = f"✅ WITHIN BUDGET: {currency_symbol}{difference:.2f} remaining under budget (Total: {currency_symbol}{total_estimated_trip_cost:.2f} of {currency_symbol}{total_budget:.2f})"
        budget_status = "WITHIN_BUDGET"

    return {
        "budget_status": budget_status,
        "is_over_budget": is_over_budget,
        "warning_indicator": warning_indicator,
        "total_budget": total_budget,
        "total_estimated_cost": total_estimated_trip_cost,
        "difference": difference,
        "overage_amount": overage_amount,
        "breakdown": {
            "lodging_cost": total_lodging_cost,
            "lodging_rate_per_night": lodging_price_per_night,
            "nights": num_nights,
            "daily_expenses_total": total_daily_expenses,
            "daily_per_person_rate": estimated_daily_expenses_per_person,
            "party_size": party_size,
            "cost_per_person": cost_per_person,
        },
    }
