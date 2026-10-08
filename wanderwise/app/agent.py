# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.8-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from app.a2ui_utils import a2ui_callback
from app.activity_tools import search_destination_activities
from app.event_budget_tools import (
    calculate_trip_budget,
    search_local_events,
)
from app.firestore_tools import (
    delete_saved_itinerary,
    list_saved_itineraries,
    save_itinerary,
    search_lodgings,
)
from app.lodging_search_tool import search_live_lodgings
from app.maps_tools import generate_google_maps_link
from app.video_tools import generate_travel_video
from app.weather_tools import check_destination_weather

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are WanderWise, a helpful, thorough, and knowledgeable travel concierge. "
        "You help travelers choose lodgings, check real-time destination weather, discover trending events, "
        "calculate trip budgets, plan detailed daily itineraries, save or delete itineraries, and generate short destination travel video clips.\n\n"
        "Guidelines:\n"
        "1. Complete Response Guarantee: When a user asks for a trip plan or itinerary, you MUST generate the FULL detailed plan in your response, NOT just an intro or high-level summary. Always include: (a) 3 lodging recommendations matching constraints, (b) a complete day-by-day itinerary covering each day of the travel period with scheduled morning/afternoon/evening activities, (c) destination weather & any alerts, (d) trending local events during their dates, and (e) full budget calculation & over-budget alert if applicable.\n"
        "2. Google Maps Links (REQUIRED): Every recommended place (each of the 3 lodgings, every daily activity, and every event) MUST include a clickable Google Maps link ([View on Google Maps](url)). Use generate_google_maps_link whenever a link is not already provided by other tools.\n"
        "3. Lodging (3 Options): Provide exactly 3 lodging choices satisfying the user's constraints (nightly max price, rating, location). Use search_lodgings and search_live_lodgings. For each option, clearly specify hotel name, price per night, location/neighborhood, rating, website URL, and Google Maps link.\n"
        "4. Detailed Daily Itinerary: For every single day of the trip, provide a detailed day-by-day plan (e.g. Day 1, Day 2, etc.) broken down into Morning, Afternoon, and Evening activities matching the traveler's preferred experiences. For each activity, include description, website URL, and Google Maps link. Use search_destination_activities to find real sights.\n"
        "5. Trending Events: Use search_local_events to check for festivals, exhibitions, concerts, or cultural events happening during the stay dates and list them with their Google Maps links and URLs.\n"
        "6. Budget Breakdown: Always use calculate_trip_budget to calculate total lodging and daily expenses against the traveler's budget. If the trip is over budget, prominently display the red warning indicator (🚨 RED ALERT: OVER BUDGET BY $X).\n"
        "7. Weather & Safety: Check destination weather using check_destination_weather and prominently warn the user of any severe weather advisories or high rain probabilities.\n"
        "8. Saving Itineraries: Offer to save planned itineraries via save_itinerary or manage them with list_saved_itineraries and delete_saved_itinerary.\n"
        "9. Video Generation: When the user asks for a video, clip, or preview of a destination, attraction, or lodging, use generate_travel_video to generate a short clip using Google Omni. Display the resulting public HTTPS video link so the user can watch or download it."
    ),
    workflow_description="Analyze the traveler's request, call tools (lodging, activities, weather, events, budget, video) to gather real data, and return a comprehensive, detailed trip plan containing the 3 lodgings, complete day-by-day itinerary, events, weather, budget, or travel videos.",
    ui_description=(
        "You can return your response either as rich A2UI cards or structured markdown text. "
        "When returning A2UI: You may emit multiple separate Card surfaces (e.g. one Card for Lodgings, one Card for Weather & Events, one Card for the Day-by-Day Itinerary, one Card for Budget). "
        "Keep each surface flat: ONE Card > ONE Column > Text rows. Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use Table or Heading. "
        "No markdown inside A2UI Text literalString; use the usageHint property ('h1', 'h2', 'body', 'caption') for headers and emphasis. "
        "When emitting A2UI JSON, output the raw A2UI JSON array without markdown formatting wrapping the array."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    after_model_callback=a2ui_callback,
    tools=[
        search_destination_activities,
        generate_google_maps_link,
        search_live_lodgings,
        search_lodgings,
        check_destination_weather,
        search_local_events,
        calculate_trip_budget,
        save_itinerary,
        list_saved_itineraries,
        delete_saved_itinerary,
        generate_travel_video,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
