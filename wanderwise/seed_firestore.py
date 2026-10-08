"""Seed initial lodging catalog items into Firestore."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-66358bebd184"

SEEDED_LODGINGS = [
    {
        "id": "tokyo-shinjuku-granbell",
        "name": "Granbell Hotel Shinjuku",
        "destination": "Tokyo",
        "location": "Kabukicho, Shinjuku, Tokyo",
        "price_per_night": 140.0,
        "rating": 4.3,
        "amenities": ["Free WiFi", "Rooftop Bar", "Terrace", "Near Subway"],
        "url": "https://www.granbellhotel.jp/en/shinjuku/",
        "maps_url": "https://maps.google.com/?q=Granbell+Hotel+Shinjuku+Tokyo",
        "description": "Modern boutique hotel in vibrant Shinjuku, walking distance to major train hubs.",
    },
    {
        "id": "tokyo-ginza-edition",
        "name": "The Tokyo EDITION, Ginza",
        "destination": "Tokyo",
        "location": "Ginza, Chuo City, Tokyo",
        "price_per_night": 480.0,
        "rating": 4.8,
        "amenities": ["Luxury Spa", "Fine Dining", "Cocktail Bar", "Concierge"],
        "url": "https://www.editionhotels.com/tokyo-ginza/",
        "maps_url": "https://maps.google.com/?q=The+Tokyo+EDITION+Ginza",
        "description": "High-end luxury urban oasis nestled right off Ginza's world-famous shopping avenue.",
    },
    {
        "id": "tokyo-asahi-ryokan",
        "name": "Asakusa Traditional Ryokan Ryokan Kaminarimon",
        "destination": "Tokyo",
        "location": "Asakusa, Taito City, Tokyo",
        "price_per_night": 110.0,
        "rating": 4.5,
        "amenities": ["Tatami Rooms", "Japanese Breakfast", "Onsen-style Bath", "Near Senso-ji"],
        "url": "https://kaminarimon.example.com",
        "maps_url": "https://maps.google.com/?q=Kaminarimon+Ryokan+Asakusa+Tokyo",
        "description": "Authentic Japanese traditional inn experience steps from historic Senso-ji Temple.",
    },
    {
        "id": "paris-le-marais-boutique",
        "name": "Hôtel Dupond-Smith Marais",
        "destination": "Paris",
        "location": "Le Marais, 4th Arrondissement, Paris",
        "price_per_night": 260.0,
        "rating": 4.7,
        "amenities": ["Quiet Courtyard", "Boutique Design", "Breakfast in Bed", "Near Art Galleries"],
        "url": "https://hoteldupondsmith.com",
        "maps_url": "https://maps.google.com/?q=Hotel+Dupond-Smith+Paris",
        "description": "Intimate luxury boutique hotel tucked in historic cobblestone alleys of Le Marais.",
    },
    {
        "id": "paris-montmartre-cozy",
        "name": "Hôtel des Arts Montmartre",
        "destination": "Paris",
        "location": "Montmartre, 18th Arrondissement, Paris",
        "price_per_night": 135.0,
        "rating": 4.6,
        "amenities": ["Panoramic Views", "Breakfast Buffet", "Near Sacré-Cœur"],
        "url": "https://www.arts-hotel-paris.com",
        "maps_url": "https://maps.google.com/?q=Hotel+des+Arts+Montmartre+Paris",
        "description": "Charming family-run hotel with views over Parisian rooftops near the Sacré-Cœur basilica.",
    },
    {
        "id": "sf-hotel-zelos",
        "name": "Hotel Zelos San Francisco",
        "destination": "San Francisco",
        "location": "SoMa / Union Square, San Francisco, CA",
        "price_per_night": 195.0,
        "rating": 4.4,
        "amenities": ["Fitness Center", "Patio Restaurant Dirty Habit", "Pet Friendly"],
        "url": "https://www.viceroyhotelsandresorts.com/zelos",
        "maps_url": "https://maps.google.com/?q=Hotel+Zelos+San+Francisco",
        "description": "Upscale stylish boutique hotel in the heart of San Francisco near museums and transit.",
    },
]


def seed_database():
    """Seed the lodgings collection in Firestore."""
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection("lodgings")

    for item in SEEDED_LODGINGS:
        doc_id = item["id"]
        doc_ref = collection.document(doc_id)
        data = {k: v for k, v in item.items() if k != "id"}
        doc_ref.set(data)
        print(f"Seeded lodging: [{item['destination']}] {item['name']} (${item['price_per_night']}/night, {item['rating']}★)")

    print(f"Successfully seeded {len(SEEDED_LODGINGS)} lodgings into Firestore collection 'lodgings'!")


if __name__ == "__main__":
    seed_database()
