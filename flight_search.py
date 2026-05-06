import requests
import os
import logging
from dotenv import load_dotenv
from flight_data import FlightData

load_dotenv()

logger = logging.getLogger(__name__)

TEQUILA_ENDPOINT = "https://api.tequila.kiwi.com"


class FlightSearch:
    """Searches for cheap flights using the Kiwi Tequila API."""

    def __init__(self):
        self.api_key = os.getenv("TEQUILA_API_KEY", "")
        if not self.api_key:
            raise EnvironmentError(
                "TEQUILA_API_KEY is not set. Add it to your .env file.\n"
                "Get a free key at https://partners.kiwi.com/"
            )

    @property
    def _headers(self):
        return {"apikey": self.api_key}

    def check_flights(self, origin, destination, from_time, to_time, currency="GBP", nights_min=7, nights_max=28):
        """
        Search for the cheapest round-trip flight between origin and destination
        departing within [from_time, to_time].

        Returns a FlightData instance or None if no flights found.
        """
        params = {
            "fly_from": origin,
            "fly_to": destination,
            "date_from": from_time.strftime("%d/%m/%Y"),
            "date_to": to_time.strftime("%d/%m/%Y"),
            "nights_in_dst_from": nights_min,
            "nights_in_dst_to": nights_max,
            "flight_type": "round",
            "one_for_city": 1,
            "max_stopovers": 0,
            "curr": currency,
            "sort": "price",
            "asc": 1,
            "limit": 1,
        }

        try:
            response = requests.get(
                url=f"{TEQUILA_ENDPOINT}/v2/search",
                headers=self._headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error("API request failed for %s→%s: %s", origin, destination, e)
            return None

        try:
            data = response.json()["data"][0]
        except (IndexError, KeyError):
            logger.info("No flights found for %s→%s", origin, destination)
            return None

        try:
            route = data["route"]
            flight = FlightData(
                price=data["price"],
                currency=currency,
                origin_city=route[0]["cityFrom"],
                origin_airport=route[0]["flyFrom"],
                destination_city=route[0]["cityTo"],
                destination_airport=route[0]["flyTo"],
                out_date=route[0]["local_departure"].split("T")[0],
                return_date=route[-1]["local_departure"].split("T")[0],
                deep_link=data.get("deep_link", ""),
            )
        except (KeyError, IndexError) as e:
            logger.error("Unexpected API response structure for %s→%s: %s", origin, destination, e)
            return None

        logger.info(
            "%s→%s: %s %.2f (budget: %.2f)",
            origin, destination, currency, flight.price, flight.price
        )
        return flight
