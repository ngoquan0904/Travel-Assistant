from config.model import model
class TravelSummary():
    def __init__(self):
        self.model = model
    def get_flight_summary(self, flight, requirements, **kwargs):
        "Get LLM summary of flight"
        print(flight)
        response = self.model.invoke(
            f"""Summarize the following flight and give me a nicely formatted output: 
            
            Given this information:
            Flights: {flight}
            
            
            Make a recommendation for the **best single outbound flight** and the **best single return flight** based on this: {requirements} {kwargs}

            Calculate the total price of the flight, which is the sum of the outbound and return flight prices.
            **Note**: If the prices of the outbound and return flights are the same, assume that the price represents the total price for the round trip.
            Only used basic markdown formatting in your reply so it can be easily parsed by the frontend.
            """
        )
        return response.content 
    
    def get_hotel_summary(self, hotels, requirements, **kwargs):
        """Get LLM summary of flights and hotels"""
        response = self.model.invoke(
            f"""Summarize the following hotels, including the total price for the duration of the stay, and give me a nicely formatted output: 
            
            Given this information:
            Hotels: {hotels}
            
            Make a recommendation for the best hotel based on this: {requirements} {kwargs}
            
            Calculate the total price for the duration of the stay based on the provided information. The duration is from {kwargs.get('start_date', 'unknown start date')} to {kwargs.get('end_date', 'unknown end date')}.
            
            Only used basic markdown formatting in your reply so it can be easily parsed by the frontend.
            """
        )
        return response.content  

# travel_summary = TravelSummary()
# flights = "Flights: Outbound: Departure: 11:00 PM Sun, Apr 20 Arrival: 12:15 PM+1 Mon, Apr 21 Airlines: French bee, Air Caraibes Duration: 7h 15m Origin: EWR (Newark Liberty International Airport) Destination: ORY (Paris Orly Airport) Price: ₫15,186,108 Stops: Nonstop Return: Departure: 6:50 PM Fri, Apr 25 Arrival: 9:00 PM Fri, Apr 25 Airlines: French bee, Air Caraibes Duration: 8h 10m Origin: ORY (Paris Orly Airport) Destination: EWR (Newark Liberty International Airport) Price: ₫15,186,108 Stops: Nonstop"

# requirements = """I want to fly from New York to Paris on April 20, 2025, and return to New York on April 25. With economy class tickets from American Airlines."""
# print(travel_summary.get_flight_summary(flights, requirements))