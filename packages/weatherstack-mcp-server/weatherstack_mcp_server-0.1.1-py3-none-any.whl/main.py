from typing import Union, Optional

from mcp.server.fastmcp import Context
from mcp.types import CallToolResult, TextContent

from config import mcp
from exceptions import WeatherstackAPIError
from api_requests import (
    get_current_weather,
    get_daily_historical_weather,
    get_hourly_historical_weather,
    get_forecast,
    get_marine_weather,
)


@mcp.tool()
async def query_current_weather(
    query: str,
    ctx: Context,
    units: str = "m",
) -> Union[dict, CallToolResult]:
    """
    Gets the current weather for a specified location using the Weatherstack API.

    Parameters:
        query (str): The location to retrieve weather data for.
            Supported formats:
            - City name (e.g. "New York")
            - ZIP code (UK, Canada, US) (e.g. "99501")
            - Latitude,Longitude coordinates (e.g. "40.7831,-73.9712")
            - IP address (e.g. "153.65.8.20")
            - Special keyword "fetch:ip" to auto-detect requester IP
        units (str, optional): The unit system to use. Defaults to "m".
            - "m" for Metric
            - "s" for Scientific
            - "f" for Fahrenheit

    Returns:
        Union[dict, CallToolResult]: A dictionary containing the current weather data,
        or a CallToolResult with an error message if the request fails.
    """
    api_key = ctx.request_context.lifespan_context.api_key

    try:
        data = await get_current_weather(query, api_key, units)
    except WeatherstackAPIError as e:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=f"Weatherstack API Error {e}")],
        )

    return data


@mcp.tool()
async def query_daily_historical_weather(
    query: str, historical_dates: list[str], ctx: Context, units: str = "m"
) -> Union[dict, CallToolResult]:
    """
    Gets daily historical weather data for a specified location and list of dates using the Weatherstack API.

    Parameters:
        query (str): The location to retrieve weather data for.
            Supported formats:
            - City name (e.g. "New York")
            - ZIP code (UK, Canada, US) (e.g. "99501")
            - Latitude,Longitude coordinates (e.g. "40.7831,-73.9712")
            - IP address (e.g. "153.65.8.20")
            - Special keyword "fetch:ip" to auto-detect requester IP
        historical_dates (list[str]): A list of historical dates in 'YYYY-MM-DD' format.
        units (str, optional): The unit system to use. Defaults to "m".
            - "m" for Metric
            - "s" for Scientific
            - "f" for Fahrenheit

    Returns:
        Union[dict, CallToolResult]: A dictionary containing the historical weather data,
        or a CallToolResult with an error message if the request fails.
    """

    api_key = ctx.request_context.lifespan_context.api_key

    try:
        historical_dates_str = ";".join(historical_dates)
        data = await get_daily_historical_weather(
            query, historical_dates_str, api_key, units
        )
    except WeatherstackAPIError as e:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=f"Weatherstack API Error {e}")],
        )

    return data


@mcp.tool()
async def query_hourly_historical_weather(
    query: str,
    historical_dates: list[str],
    ctx: Context,
    units: str = "m",
    interval: int = 3,
) -> Union[dict, CallToolResult]:
    """
    Gets hourly historical weather data for a specified location and list of dates using the Weatherstack API.

    Parameters:
        query (str): The location to retrieve weather data for.
            Supported formats:
            - City name (e.g. "New York")
            - ZIP code (UK, Canada, US) (e.g. "99501")
            - Latitude,Longitude coordinates (e.g. "40.7831,-73.9712")
            - IP address (e.g. "153.65.8.20")
            - Special keyword "fetch:ip" to auto-detect requester IP
        historical_dates (list[str]): A list of historical dates in 'YYYY-MM-DD' format.
        units (str, optional): The unit system to use. Defaults to "m".
            - "m" for Metric
            - "s" for Scientific
            - "f" for Fahrenheit
        interval (int, optional): The interval for hourly data aggregation. Defaults to 3.
            Supported values:
            - 1 for hourly
            - 3 for 3-hourly (default)
            - 6 for 6-hourly
            - 12 for 12-hourly (day/night)
            - 24 for daily average


    Returns:
        Union[dict, CallToolResult]: A dictionary containing the historical weather data,
        or a CallToolResult with an error message if the request fails.
    """

    api_key = ctx.request_context.lifespan_context.api_key

    try:
        historical_dates_str = ";".join(historical_dates)
        data = await get_hourly_historical_weather(
            query, historical_dates_str, api_key, units, interval
        )
    except WeatherstackAPIError as e:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=f"Weatherstack API Error {e}")],
        )

    return data


@mcp.tool()
async def query_forecast(
    query: str, forecast_days: int, ctx: Context
) -> Union[dict, CallToolResult]:
    """
    Gets weather forecast data for a specified location and number of days using the Weatherstack API.

    Parameters:
        query (str): The location to retrieve forecast data for.
            Supported formats:
            - City name (e.g. "New York")
            - ZIP code (UK, Canada, US) (e.g. "99501")
            - Latitude,Longitude coordinates (e.g. "40.7831,-73.9712")
            - IP address (e.g. "153.65.8.20")
            - Special keyword "fetch:ip" to auto-detect requester IP
        forecast_days (int): The number of days to retrieve forecast data for.
            Maximum allowed is 21.

    Returns:
        Union[dict, CallToolResult]: A dictionary containing the forecast weather data,
        or a CallToolResult with an error message if the request fails.
    """
    api_key = ctx.request_context.lifespan_context.api_key

    try:
        forecast_data = await get_forecast(query, forecast_days, api_key)
    except WeatherstackAPIError as e:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=f"Weatherstack API Error {e}")],
        )

    return forecast_data


@mcp.tool()
async def query_marine_weather(
    lat: float,
    lon: float,
    ctx: Context,
    units: str = "m",
    interval: Optional[int] = None,
) -> Union[dict, CallToolResult]:
    """
    Gets live marine/sailing weather data and up to 7 days of forecast for a specified location 
    (by latitude and longitude) using the Weatherstack API.

    This tool accesses today's live marine weather forecast as well as forecasts for up to 7 days 
    into the future for the given coordinates. It is useful for sailing, fishing, boating, and 
    coastal activity planning.

    Parameters:
        lat (float): The latitude of the location to retrieve marine weather data for.
        lon (float): The longitude of the location to retrieve marine weather data for.
        units (str, optional): The unit system to use. Defaults to "m".
            - "m" for Metric
            - "s" for Scientific
            - "f" for Fahrenheit
        interval (int, optional): Optional interval for forecast data granularity, if supported by the API.

    Returns:
        Union[dict, CallToolResult]: A dictionary containing the marine weather data,
        or a CallToolResult with an error message if the request fails.
    """
    api_key = ctx.request_context.lifespan_context.api_key

    try:
        marine_weather_data = await get_marine_weather(
            lat, lon, api_key, units, interval
        )
    except WeatherstackAPIError as e:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=f"Weatherstack API Error {e}")],
        )

    return marine_weather_data


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
