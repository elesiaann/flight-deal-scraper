import json
import logging

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {"origin", "destination", "max_price", "currency"}


class DataManager:
    """Loads and validates watched routes from routes.json."""

    def __init__(self, routes_file="routes.json"):
        self.routes_file = routes_file
        self.destination_data = []

    def get_destination_data(self):
        with open(self.routes_file, encoding="utf-8") as f:
            routes = json.load(f)

        validated = []
        for i, route in enumerate(routes):
            missing = REQUIRED_KEYS - route.keys()
            if missing:
                logger.warning("Route #%d skipped — missing keys: %s", i, missing)
                continue
            if not isinstance(route["max_price"], (int, float)) or route["max_price"] <= 0:
                logger.warning("Route #%d skipped — max_price must be a positive number", i)
                continue
            if len(route["origin"]) != 3 or len(route["destination"]) != 3:
                logger.warning("Route #%d skipped — origin/destination must be 3-letter IATA codes", i)
                continue
            validated.append({
                "origin": route["origin"].upper(),
                "destination": route["destination"].upper(),
                "max_price": route["max_price"],
                "currency": route["currency"].upper(),
                "nights_min": route.get("nights_min", 7),
                "nights_max": route.get("nights_max", 28),
            })

        self.destination_data = validated
        logger.info("Loaded %d route(s) from %s", len(validated), self.routes_file)
        return validated
