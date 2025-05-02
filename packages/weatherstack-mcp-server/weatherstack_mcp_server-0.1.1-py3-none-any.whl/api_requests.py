from typing import Optional

from httpx import AsyncClient, HTTPStatusError, RequestError

from exceptions import WeatherstackAPIError

WEATHERSTACK_BASE_URL = "http://api.weatherstack.com"


async def _safe_request(
    method: str,
    url: str,
    **kwargs: dict,
) -> dict:
    async with AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except HTTPStatusError as e:
            raise WeatherstackAPIError(
                f"API error {e.response.status_code} at {url}: {e.response.text}"
            ) from e

        except RequestError as e:
            raise WeatherstackAPIError(
                f"Network error during request to {url}: {str(e)}"
            ) from e

        except Exception as e:
            raise WeatherstackAPIError(
                f"Unexpected error during request to {url}: {str(e)}"
            ) from e


async def get_current_weather(query: str, api_key: str, units: str) -> dict:
    url = f"{WEATHERSTACK_BASE_URL}/current"
    params = {"access_key": api_key, "query": query, "units": units}
    return await _safe_request("GET", url, params=params)


async def get_historical_weather(
    query: str,
    historical_date: str,
    api_key: str,
    units: str,
    interval: Optional[int] = None,
) -> dict:
    url = f"{WEATHERSTACK_BASE_URL}/historical"
    params = {
        "access_key": api_key,
        "query": query,
        "historical_date": historical_date,
        "units": units,
    }
    if interval:
        params["hourly"] = 1
        params["interval"] = interval

    return await _safe_request("GET", url, params=params)


async def get_daily_historical_weather(
    query: str, historical_date: str, api_key: str, units: str
) -> dict:
    return await get_historical_weather(query, historical_date, api_key, units)


async def get_hourly_historical_weather(
    query: str, historical_date: str, api_key: str, units: str, interval: int
) -> dict:
    return await get_historical_weather(
        query, historical_date, api_key, units, interval
    )


async def get_forecast(query: str, forecast_days: int, api_key: str) -> dict:
    url = f"{WEATHERSTACK_BASE_URL}/forecast"
    params = {
        "access_key": api_key,
        "query": query,
        "forecast_days": forecast_days,
    }
    return await _safe_request("GET", url, params=params)


async def get_marine_weather(
    lat: float, lon: float, api_key: str, units: str, interval: Optional[int]
) -> dict:
    url = f"{WEATHERSTACK_BASE_URL}/marine"
    params = {
        "tide": "yes",
        "access_key": api_key,
        "latitude": lat,
        "longitude": lon,
        "units": units,
    }
    if interval:
        params["hourly"] = 1
        params["interval"] = interval
    return await _safe_request("GET", url, params=params)
