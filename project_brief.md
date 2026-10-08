# My agent: WanderWise (Travel Concierge)
One-liner: A conversational agent that helps travelers plan personalized trips and daily itineraries with a catalog of lodging choices, local activities, trending events, and saved trip itineraries.

Tool coverage:
- Memory: Remembers traveler party details (party size, travel style, past trips, dietary restrictions, accommodation preferences, lodging price caps, and minimum ratings).
- Tools: Lodging search (filters by nightly max price, area, and review rating), itinerary activity lookup (with website URLs & Google Maps links), trending local event finder, live weather/severe weather alert checker, and itinerary persistence tools (save new itinerary, list saved itineraries, and delete selected itinerary).
- Catalog/UI: Lodging recommendation cards (3 options showing price, location, rating, photos, and links), daily itinerary schedules / activity tables, saved trips catalog (with option to view or delete), and budget breakdown cards with red warning alerts if total cost exceeds user budget.
- Image gen: Generates custom destination postcards or visual vibe moodboards for the planned itinerary.
- Sandbox: Computes total trip budget breakdown across party members, per-night totals, and currency conversions against the user's budget cap.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for budget overage calculations & currency conversion, live weather alert API, Google Maps URL generation, Firestore/Cloud Storage for itinerary persistence (CRUD).
