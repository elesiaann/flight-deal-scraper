# Flight Deal Scraper

Alert when flight prices drop below your budget! This tool searches for the cheapest flights from your origin city to various destinations within a 6-month window.

## Features
- Automatically finds IATA codes for cities.
- Searches for round-trip flights with a stay between 7 and 28 days.
- Sends email alerts when a deal is found.
- Supports Google Sheets (via Sheety) or local data management.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/elesiaann/flight-deal-scraper
   cd flight-deal-scraper
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   - Copy `.env.example` to `.env`.
   - Get a free API Key from [Kiwi Tequila](https://partners.kiwi.com/).
   - (Optional) Set up a Google Sheet with columns: `City`, `IATA Code`, `Lowest Price`.
   - Update `.env` with your API keys and email settings.

4. **Run the Scraper:**
   ```bash
   python main.py
   ```

## Project Structure
- `main.py`: Entry point and orchestration.
- `flight_search.py`: Interacts with the Kiwi Tequila API.
- `data_manager.py`: Manages destination data.
- `flight_data.py`: Data structure for flight information.
- `notification_manager.py`: Handles email alerts.
