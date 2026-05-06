"""
Flight Deal Scraper
-------------------
Periodically checks Kiwi Tequila for cheap flights across your watched routes
and sends an email alert when a price drops below your budget.

Usage:
    python main.py              # runs on the configured interval (default: 60 min)
    python main.py --once       # run a single check and exit
"""
import logging
import sys
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

import storage
from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

# ── configuration ────────────────────────────────────────────────────────────
import os
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))
SEARCH_WINDOW_DAYS = int(os.getenv("SEARCH_WINDOW_DAYS", "180"))  # 6 months ahead


# ── core check ───────────────────────────────────────────────────────────────
def check_all_routes():
    logger.info("Starting deal check …")

    data_manager = DataManager()
    routes = data_manager.get_destination_data()

    flight_search = FlightSearch()
    notifier = NotificationManager()

    from_time = datetime.now() + timedelta(days=1)
    to_time = datetime.now() + timedelta(days=SEARCH_WINDOW_DAYS)

    deals_found = 0

    for route in routes:
        origin = route["origin"]
        destination = route["destination"]
        max_price = route["max_price"]
        currency = route["currency"]
        nights_min = route["nights_min"]
        nights_max = route["nights_max"]

        flight = flight_search.check_flights(
            origin=origin,
            destination=destination,
            from_time=from_time,
            to_time=to_time,
            currency=currency,
            nights_min=nights_min,
            nights_max=nights_max,
        )

        if flight is None:
            continue

        if flight.price >= max_price:
            logger.info(
                "%s→%s: %s%.2f — above budget (%s%.2f), skipping",
                origin, destination, currency, flight.price, currency, max_price,
            )
            continue

        # Deal found — check deduplication
        if storage.has_alert_been_sent(origin, destination, flight.out_date, flight.price):
            logger.info(
                "%s→%s: %s%.2f — already alerted, skipping",
                origin, destination, currency, flight.price,
            )
            continue

        logger.warning(
            "DEAL: %s→%s %s%.2f (budget %s%.2f) departing %s",
            origin, destination, currency, flight.price, currency, max_price, flight.out_date,
        )

        notifier.send_deal_alert(flight)
        storage.record_alert(origin, destination, flight.out_date, flight.price, currency)
        deals_found += 1

    logger.info("Check complete — %d deal(s) alerted.", deals_found)


# ── entry point ───────────────────────────────────────────────────────────────
def main():
    storage.bootstrap_schema()

    run_once = "--once" in sys.argv

    if run_once:
        check_all_routes()
        return

    logger.info("Scheduler starting — checking every %d minute(s).", CHECK_INTERVAL_MINUTES)
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        check_all_routes,
        trigger="interval",
        minutes=CHECK_INTERVAL_MINUTES,
        next_run_time=datetime.utcnow(),  # run immediately on start
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Shutting down.")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
