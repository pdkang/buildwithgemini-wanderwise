"""Firestore database backend and tools for WanderWise Travel Concierge."""

from typing import Any
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-66358bebd184"

_db = None


def get_firestore_client() -> firestore.Client:
    """Return a Firestore client initialized with the hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def search_lodgings(
    destination: str | None = None,
    max_price_per_night: float | None = None,
    min_rating: float | None = None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Search available lodging choices in Firestore meeting the traveler's criteria.

    Args:
        destination: City or region to search (case-insensitive substring match).
        max_price_per_night: Maximum acceptable lodging cost per night.
        min_rating: Minimum review score rating (out of 5.0).
        limit: Maximum number of options to return (default 3).

    Returns:
        A list of matching lodging records with name, location, price, rating, and details.
    """
    db = get_firestore_client()
    query = db.collection("lodgings")

    docs = query.stream()
    results = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        if destination and destination.lower() not in data.get("destination", "").lower() and destination.lower() not in data.get("location", "").lower():
            continue

        if max_price_per_night is not None and data.get("price_per_night", 0) > max_price_per_night:
            continue

        if min_rating is not None and data.get("rating", 0) < min_rating:
            continue

        results.append(data)
        if len(results) >= limit:
            break

    return results


def save_itinerary(
    title: str,
    destination: str,
    travel_period: str,
    party_size: int,
    total_budget: float,
    lodging_id: str | None = None,
    days: list[dict[str, Any]] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Save a planned trip itinerary to Firestore for the traveler.

    Args:
        title: Title for the itinerary (e.g. 'Tokyo Cherry Blossom 5-Day Trip').
        destination: Travel destination city or region.
        travel_period: Dates or duration of the trip (e.g. '2026-11-01 to 2026-11-06').
        party_size: Number of people traveling.
        total_budget: User's total trip budget.
        lodging_id: Optional ID or name of the chosen lodging.
        days: Daily list of activities, URLs, Google Maps links, and notes.
        notes: Additional remarks or weather advisories.

    Returns:
        A dictionary containing the saved itinerary id and confirmation status.
    """
    db = get_firestore_client()
    doc_ref = db.collection("itineraries").document()
    itinerary_data = {
        "title": title,
        "destination": destination,
        "travel_period": travel_period,
        "party_size": party_size,
        "total_budget": total_budget,
        "lodging_id": lodging_id,
        "days": days or [],
        "notes": notes,
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    doc_ref.set(itinerary_data)
    return {"status": "saved", "itinerary_id": doc_ref.id, "title": title}


def list_saved_itineraries(limit: int = 10) -> list[dict[str, Any]]:
    """List previously saved trip itineraries from Firestore.

    Args:
        limit: Maximum number of itineraries to retrieve.

    Returns:
        List of saved itineraries with their IDs, titles, destinations, and details.
    """
    db = get_firestore_client()
    docs = db.collection("itineraries").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream()

    items = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        if "created_at" in item and item["created_at"]:
            item["created_at"] = str(item["created_at"])
        items.append(item)
    return items


def delete_saved_itinerary(itinerary_id: str) -> dict[str, Any]:
    """Delete a saved itinerary by its ID from Firestore.

    Args:
        itinerary_id: The document ID of the itinerary to delete.

    Returns:
        Confirmation status message of the deletion.
    """
    db = get_firestore_client()
    doc_ref = db.collection("itineraries").document(itinerary_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"status": "error", "message": f"Itinerary with ID {itinerary_id} not found."}

    doc_ref.delete()
    return {"status": "deleted", "itinerary_id": itinerary_id}
