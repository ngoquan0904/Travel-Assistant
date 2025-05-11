from langchain.output_parsers import PydanticOutputParser
from datetime import datetime
from config.model import model
from pydantic import BaseModel, Field
from typing import Optional
import json
import re
def clean_json_response(response):
    """Remove markdown code block and convert to valid JSON"""
    match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
    if match:
        clean_json = match.group(1)
    else:
        clean_json = response  # If no markdown, keep as is
    
    try:
        return json.loads(clean_json)  # Convert to valid JSON
    except json.JSONDecodeError:
        raise ValueError("JSON parsing error! Check the model's output.")

# Define output schema
class FlightDetails(BaseModel):
    origin: str = Field(..., description="Origin location")
    destination: str = Field(..., description="Destination location")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    budget: Optional[str] = Field(None, description="Budget")
    ticket_class: Optional[str] = Field(None, description="Ticket class")
    airline: Optional[str] = Field(None, description="Airline")
# Create a parser to enforce valid JSON output
parser = PydanticOutputParser(pydantic_object=FlightDetails)
def correct_date_field_flight(json_data):
    dates = ["start_date", "end_date"]  # Các trường ngày cần xử lý
    for date in dates:
        date_str = json_data[date]
        try:
            # Chuyển đổi từ định dạng YYYY-MM-DD sang đối tượng datetime
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Định dạng lại ngày thành "Day, Month DD, YYYY"
            formatted_date = dt.strftime("%A, %B %d, %Y")
            json_data[date] = formatted_date
        except Exception as e:
            print(f"Date correction failed for {date}: {e}")
    return json_data
def get_flight_details(requirements):
    prompt = f"""
        Extract detailed travel information from the user's input.
        Ensure the result is returned as valid JSON in the following format:
        
        {parser.get_format_instructions()}

        User input:
        {requirements}
    """
    
    response = model.invoke(prompt).content  
    json_response = correct_date_field_flight(clean_json_response(response)  )
    return FlightDetails(**json_response) 


class HotelDetails(BaseModel):
    location: Optional[str] = Field(None, description="Location")
    check_in: Optional[str] = Field(None, description="Check-in date")
    check_out: Optional[str] = Field(None, description="Check-out date")
    price_per_night: Optional[str] = Field(None, description="Price per night with currency")
    rating: Optional[str] = Field(None, description="Hotel rating")
    amenities: Optional[str] = Field(None, description="Available amenities")
# Create parser
hotel_parser = PydanticOutputParser(pydantic_object=HotelDetails)
def get_hotel_details(summary_text):
    prompt = f"""
        Extract the most relevant hotel information from the following summary text.
        Ensure the result is returned as valid JSON in the following format:

        {hotel_parser.get_format_instructions()}

        Hotel summary:
        {summary_text}
    """
    
    response = model.invoke(prompt).content
    json_data = clean_json_response(response)
    return HotelDetails(**json_data)


class RestaurantDetails(BaseModel):
    location: Optional[str] = Field(None, description="Location of the restaurant")
    date: Optional[str] = Field(None, description="Date of the reservation")
    time: Optional[str] = Field(None, description="Time of the reservation")
    number_people: Optional[int] = Field(None, description="Number of people for the reservation")
    cuisine: Optional[str] = Field(None, description="Preferred cuisine type")
    rating: Optional[str] = Field(None, description="Minimum rating of the restaurant")
    price_range: Optional[str] = Field(None, description="Price range per person")
# Create parser
restaurant_parser = PydanticOutputParser(pydantic_object=RestaurantDetails)
def correct_date_field(json_data):
    date_str = json_data["date"]  # e.g., "Tuesday, April 17"
    # Tách phần tháng/ngày
    try:
        _, month_day = date_str.split(", ")
        full_date = f"{month_day}, 2025"  # Giả định năm
        dt = datetime.strptime(full_date, "%B %d, %Y")
        correct_day = dt.strftime("%A")
        json_data["date"] = f"{correct_day}, {month_day}"
    except Exception as e:
        print("Date correction failed:", e)
    return json_data
def get_restaurant_details(summary_text):
    prompt = f"""
        Extract the most relevant restaurant information from the following summary text.
        Ensure the result is returned as valid JSON in the following format:

        {restaurant_parser.get_format_instructions()}

        Notes:
        - The "date" field should be in the format "Day, Month DD" (e.g., "Thursday, April 17") and "Day" corresponds to the actual date.
        - The "time" field should be in the format "HH:MM AM/PM" (e.g., "6:00 PM").

        Restaurant summary:
        {summary_text}
    """
    
    response = model.invoke(prompt).content
    json_data = correct_date_field(clean_json_response(response))
    return RestaurantDetails(**json_data)

# # Test with input
# requirements = """I want to fly from New York to Paris on May 20, 2025, and return to New York on May 25. With economy class tickets from Air France Airlines."""
# I'm planning a trip to Paris from May 20, 2025, to May 25, 2025. 
# I'm looking for a hotel with a nightly price under 3.000.000 and a rating of 4 stars or higher. 
# Amenities are not a priority, but I'd like a comfortable and well-rated place to stay.
# requirements = """
# I'm looking for a pizza place in Washington for three people on April 17. 
# We'd like to have dinner around 6 PM. The restaurant should have at least 4 stars 
# and the price should be under $50 per person.
# """
# result = get_flight_details(requirements)
# # Print the result
# print(result.model_dump_json(indent=2))