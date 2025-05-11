"""Constants for the frontend application."""

# Search Tab
TRAVEL_DESCRIPTION_HELP = "Tell us about your trip including where you're flying from/to, dates, number of travelers, and any preferences."
FLIGHT_DESCRIPTION_PLACEHOLDER = """Example: I want to fly from LAX to NYC from December 1st, 2024 to December 8th, 2024. 
Budget around $1000 for flight"""
HOTEL_DESCRIPTION_PLACEHOLDER = """Example: I'm planning a trip to Paris from May 20, 2025, to May 25, 2025. 
I'm looking for a hotel with a nightly price under 3.000.000 and a rating of 4 stars or higher."""

# Loading States
LOADING_STATES = {
    "flights": {
        "message": "✈️ Searching Flights",
        "description": """Checking airlines • Finding routes • Comparing prices"""
    },
    "hotels": {
        "message": "🏨 Finding Hotels",
        "description": """Searching rooms • Checking amenities • Comparing rates"""
    },
    "processing": {
        "message": "✨ Creating Your Trip",
        "description": """Analyzing options • Optimizing choices • Preparing summary"""
    }
}

# Results Tab
NO_TRIP_DETAILS_MESSAGE = """After you complete your trip search, you'll find:
- Flight and hotel recommendations
- Personalized travel summary
- Interactive travel planning assistant

Head over to the Search tab to start planning your trip!"""

PREVIEW_SUMMARY = """### ✈️ Travel Summary
You'll get a detailed summary of your travel options, including:
- Best flight options matching your preferences
- Hotel recommendations in your price range
- Trip timeline and logistics

### 💬 Travel Planning Assistant
Access an AI assistant that can help you:
- Compare different flight and hotel options
- Get pricing breakdowns
- Plan your itinerary
- Answer questions about your bookings"""

# Research Tab
RESEARCH_LOCKED_MESSAGE = """The research assistant will help you:
- Find local restaurants and attractions
- Learn about your destination
- Get travel tips and recommendations

Start by describing your trip in the Search tab!"""

RESEARCH_ASSISTANT_INTRO = """Research assistant for your trip.! 
Learn about local restaurants, attractions, and travel tips. This assistant can search 
the internet for up-to-date information about your destination."""

# Error Messages
MISSING_AIRPORTS_ERROR = "Please specify both departure and destination airports in your description"
MISSING_DATES_ERROR = "Please specify both departure and return dates in your description"
MISSING_DESCRIPTION_ERROR = "Please describe your travel plans"
MISSING_LOCATION_ERROR = "Please specify location in your description"
# Status Messages
SEARCH_COMPLETED = "🎉 Perfect! We've found some great options for your trip!"
SEARCH_FAILED = "😕 We couldn't start the search. Please try again."
SEARCH_INCOMPLETE = "😕 We couldn't complete the search. Please try again."
NO_SUMMARY_YET = "No travel summary available yet." 