class FlightData:
    """Holds structured data for a single cheapest-flight result."""

    def __init__(self, price, currency, origin_city, origin_airport,
                 destination_city, destination_airport, out_date, return_date, deep_link=""):
        self.price = price
        self.currency = currency
        self.origin_city = origin_city
        self.origin_airport = origin_airport
        self.destination_city = destination_city
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date
        self.deep_link = deep_link

    def __repr__(self):
        return (
            f"FlightData({self.origin_airport}→{self.destination_airport}, "
            f"{self.currency}{self.price}, {self.out_date}–{self.return_date})"
        )
