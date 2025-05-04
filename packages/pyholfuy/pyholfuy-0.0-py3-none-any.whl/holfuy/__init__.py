"""Library to handle connection with Holfuy Live API."""

import asyncio
import logging

from typing import Any

import aiohttp

from .const import (
    CONF_TEMPERATURE_UNIT_CELSUIS,
    CONF_WIND_SPEED_UNIT_MS,
    CONF_AVERAGING_NEWEST,
    CONF_MODE_JSON,
    STATIONS_ALL,
)

TIMEOUT = 30
_LOGGER = logging.getLogger(__name__)

API_URL = "http://api.holfuy.com/live/"

# noqa: E501
#### API Description
# URL Format:  http://api.holfuy.com/live/?s=101&pw=pass&m=JSON&tu=C&su=m/s
#
# s: station(s) ID e.g. s=101 or you can get the data from more stations by one query as well (coma separated list) e.g. s=101,102,103 . If you would get all stations' data (to which you have access) by one single API call please use the "all" string -> s=all .
# pw: password for the API access (it could be sent by a POST "pw" parameter also)
# m:mode XML or CSV or JSON default: CSV
# avg:averaging "0": newest data from the station, "1" newest quarter hourly average, "2" newest hourly average (default = 0)
# su: wind speed unit: knots, km/h, m/s, mph, default: m/s
# tu: temperature unit C:Celsius , F: Fahrenheit default: Celsius
# batt: add this parameter to get the station's battery voltage (JSON only).
# cam: add this parameter to the URL for timestamp of the last picture from the camera. (JSON only, only for stations with a camera)
# daily: add this parameter to get daily Max-Min temperatures and precipitation since last midnight CE(S)T (JSON only, max 5 stations)
# loc: add this parameter to the URL to get the station's location in reply too (JSON only)
# utc: add this parameter to the URL for timestamps in UTC, otherwise times will be in CE(S)T
# Data: DateTime: time of the last data / average in ".date('T')." (Central European Time) or in UTC if utc param is set.
#####


class HolfuyService:
    """Representation of Holfuy weather data."""

    def __init__(
        self,
        api_key: str,
        websession=None,
        temperature_unit=CONF_TEMPERATURE_UNIT_CELSUIS,
        wind_speed_unit=CONF_WIND_SPEED_UNIT_MS,
        timestamps_in_utc=False,
    ) -> None:
        """Initialize the Weather object."""

        self._api_url = API_URL
        self._api_key = api_key
        self._wind_speed_unit = wind_speed_unit
        self._temperature_unit = temperature_unit
        self._timestamps_in_utc = timestamps_in_utc

        if websession is None:

            async def _create_session():
                return aiohttp.ClientSession()

            loop = asyncio.get_event_loop()
            self._websession = loop.run_until_complete(_create_session())
        else:
            self._websession = websession

    async def fetch_data(
        self,
        stations: list[str] | None = None,
        averaging_mode=CONF_AVERAGING_NEWEST,
        include_battery=False,
        include_daily=False,
        include_location=False,
    ) -> dict[str, Any] | None:
        """Get the latest data from Holfuy."""

        params = {
            "pw": self._api_key,
            "m": CONF_MODE_JSON,
            "tu": self._temperature_unit,
            "su": self._wind_speed_unit,
            "avg": averaging_mode,
        }

        if self._timestamps_in_utc:
            params["utc"] = ""

        if include_battery:
            params["batt"] = ""

        if include_daily:
            params["daily"] = ""

        if include_location:
            params["loc"] = ""

        if stations:
            params["s"] = ",".join(map(str, stations))
        else:
            params["s"] = STATIONS_ALL

        try:
            async with asyncio.timeout(TIMEOUT):
                resp = await self._websession.get(self._api_url, params=params)

            if resp.status >= 400:
                _LOGGER.error("%s returned %s", self._api_url, resp.status)
                return None

            result = await resp.json()

            # Request for a single station is not enveloped in a list of
            # measurements objects. Make data consistent for all request types before it
            #  is returned.
            if stations and len(stations) == 1:
                result = {"measurements": result}

            return result

        except (TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error(
                "Access to %s returned error '%s'", self._api_url, type(err).__name__
            )
            return None
        except ValueError:
            _LOGGER.exception("Unable to parse json response from %s", self._api_url)
            return None
