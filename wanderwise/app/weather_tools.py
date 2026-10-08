"""Weather and severe weather alert tool using Open-Meteo API."""

import json
import urllib.parse
import urllib.request
from typing import Any

# WMO Weather interpretation codes (WW)
WMO_DESCRIPTIONS: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

SEVERE_WEATHER_CODES = {65, 75, 82, 86, 95, 96, 99}


def check_destination_weather(destination: str) -> dict[str, Any]:
    """Fetch live weather forecasts and severe weather alerts for a travel destination.

    Args:
        destination: City or destination name (e.g. 'Tokyo', 'Paris', 'San Francisco').

    Returns:
        Dictionary containing current weather, 5-day forecast, temperatures, and severe weather warnings.
    """
    try:
        # Step 1: Geocode city name to lat/long
        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            + urllib.parse.urlencode({"name": destination, "count": 1, "language": "en", "format": "json"})
        )
        req = urllib.request.Request(geo_url, headers={"User-Agent": "WanderWise/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            geo_data = json.loads(resp.read().decode("utf-8"))

        results = geo_data.get("results")
        if not results:
            return {"status": "error", "message": f"Could not find coordinates for destination: '{destination}'"}

        location = results[0]
        lat = location["latitude"]
        lon = location["longitude"]
        resolved_name = f"{location.get('name')}, {location.get('country')}"
        timezone = location.get("timezone", "auto")

        # Step 2: Fetch forecast & weather conditions
        forecast_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
            "timezone": timezone,
            "forecast_days": 5,
        }
        forecast_url = f"https://api.open-meteo.com/v1/forecast?{urllib.parse.urlencode(forecast_params)}"

        forecast_req = urllib.request.Request(forecast_url, headers={"User-Agent": "WanderWise/1.0"})
        with urllib.request.urlopen(forecast_req, timeout=10) as resp:
            forecast_data = json.loads(resp.read().decode("utf-8"))

        current = forecast_data.get("current", {})
        daily = forecast_data.get("daily", {})

        current_code = current.get("weather_code", 0)
        current_condition = WMO_DESCRIPTIONS.get(current_code, f"Code {current_code}")

        # Check for severe weather alerts in forecast
        alerts: list[str] = []
        if current_code in SEVERE_WEATHER_CODES:
            alerts.append(f"CURRENT SEVERE WEATHER ALERT: {current_condition} detected.")

        if current.get("wind_speed_10m", 0) > 60:
            alerts.append(f"HIGH WIND WARNING: Current wind speeds at {current.get('wind_speed_10m')} km/h.")

        daily_forecast: list[dict[str, Any]] = []
        dates = daily.get("time", [])
        codes = daily.get("weather_code", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip_probs = daily.get("precipitation_probability_max", [])
        wind_maxs = daily.get("wind_speed_10m_max", [])

        for i in range(len(dates)):
            wcode = codes[i] if i < len(codes) else 0
            wdesc = WMO_DESCRIPTIONS.get(wcode, f"Code {wcode}")
            p_prob = precip_probs[i] if i < len(precip_probs) else 0
            w_max = wind_maxs[i] if i < len(wind_maxs) else 0

            if wcode in SEVERE_WEATHER_CODES:
                alerts.append(f"Upcoming {dates[i]}: Severe weather expected ({wdesc}).")
            if p_prob > 80:
                alerts.append(f"Upcoming {dates[i]}: High probability of heavy rain ({p_prob}%).")
            if w_max > 60:
                alerts.append(f"Upcoming {dates[i]}: High winds forecast ({w_max} km/h).")

            daily_forecast.append({
                "date": dates[i],
                "condition": wdesc,
                "temp_high_c": max_temps[i] if i < len(max_temps) else None,
                "temp_low_c": min_temps[i] if i < len(min_temps) else None,
                "precip_probability_pct": p_prob,
            })

        return {
            "status": "success",
            "destination": resolved_name,
            "current_weather": {
                "temperature_c": current.get("temperature_2m"),
                "feels_like_c": current.get("apparent_temperature"),
                "condition": current_condition,
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "humidity_pct": current.get("relative_humidity_2m"),
            },
            "alerts": alerts,
            "has_severe_alert": len(alerts) > 0,
            "daily_forecast": daily_forecast,
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch live weather: {str(e)}"}
