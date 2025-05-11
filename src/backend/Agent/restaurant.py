from playwright.async_api import async_playwright
from browser_use import Agent, Browser, BrowserConfig
from config.model import model

def restaurant_scrape_task(preferences, url):
    return f"""You are an assistant helping scrape restaurant data from TripAdvisor.

    1. Go to the following URL: {url}
    2. Use the search bar to look for restaurants that include {preferences['cuisine']} in their cuisine types and click "Find a table".
    3. Filter results based on the following preferences:
        - Rating: {preferences['rating']}
        - Price Range: {preferences['price_range']}
    4. Identify ONE best-matching restaurant.
    5. Extract the following details:
        * Restaurant name
        * Rating
        * Number of reviews
        * Price range
        * Address
        * Type of cuisine
        * Opening hours (if available)
        * Meal type (e.g., breakfast, lunch, dinner)
        * Top amenities or highlights (if available)

    6. Only return one restaurant that best fits the preferences.
    """
class RestaurantSearchScraper:
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
    
    async def fill_restaurant_search(self, location=None, date=None, time=None, num_people=None):
        try:
            print("Navigating to OpenTable...")
            await self.page.goto("https://www.opentable.com/")
            await self.page.wait_for_timeout(2000)

            if date:
                print("Selecting date...")
                date_button = await self.page.wait_for_selector('[aria-label="Date selector"]', timeout=5000)
                await date_button.click()
                
                await self.page.wait_for_selector('#search-autocomplete-day-picker-wrapper', timeout=5000)
                
                date_selector = f'button[aria-label="{date}"]'
                selected_date_button = await self.page.wait_for_selector(date_selector, timeout=5000)
                await selected_date_button.click()
                
                await self.page.wait_for_timeout(1000)

            if time:
                print("Selecting time...")
                try:
                    # Tìm dropdown selector cho thời gian
                    time_select = await self.page.wait_for_selector('select[aria-label="Time selector"]', timeout=5000)
                    await time_select.select_option(label=time)
                    print(f"Time '{time}' selected successfully.")
                except Exception as e:
                    print(f"Failed to select time '{time}': {str(e)}")
                
                await self.page.wait_for_timeout(1000)

            if num_people:
                print("Selecting number of people...")
                party_select = await self.page.wait_for_selector('select[aria-label="Party size selector"]', timeout=5000)
                await party_select.select_option(str(num_people))

            if location:
                print("Filling in location...")
                location_input = await self.page.wait_for_selector(
                    '#home-page-autocomplete-input', timeout=8000
                )
                await location_input.click()
                await location_input.fill(location)
                await location_input.press("Enter")
                await self.page.wait_for_timeout(2000)

            await self.page.wait_for_timeout(1000)
            print(f"Final URL: {self.page.url}")
            return self.page.url

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
    async def close(self):
        try:
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    
async def scrape_restaurant(url, preferences):
    browser = Browser(
        config=BrowserConfig(
            chrome_instance_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        )
    )
    initial_actions = [
        {"open_tab": {"url": url}},
    ]
    agent = Agent(
        task=restaurant_scrape_task(preferences, url),
        llm=model,
        initial_actions=initial_actions,
        browser=browser,
    )
    history = await agent.run()
    await browser.close()
    result = history.final_result()
    return result
async def get_restaurant_url(date, time, num_people, location):
    try:
        scraper = RestaurantSearchScraper()
        await scraper.start()
        url = await scraper.fill_restaurant_search(location=location, date=date, time=time, num_people=num_people)
        return url
    finally:
        print("closing connection...")
        if "scraper" in locals():
            await scraper.close()
    return None
# # ✅ Preferences: Clearer vocabulary
# location = "Washington"
# date = "Thursday, April 17"
# time = "6:00 PM"
# number_people = 3
# cuisine = "pizza"
# rating = "4 stars and up"
# price_range = "under $50 per person"

# preferences = {
#     "cuisine": cuisine,
#     "rating": rating,
#     "price_range": price_range,
# }

# restaurant_url = asyncio.run(get_restaurant_url(date, time, number_people, location))
# if restaurant_url:
#     print(f"Restaurant search URL: {restaurant_url}")
#     result = asyncio.run(scrape_restaurant(restaurant_url, preferences))
    
#     # Kiểm tra và in thông tin chi tiết nhà hàng
#     if result and hasattr(result, 'final_result'):
#         final_result = result.final_result
#         if isinstance(final_result, str):
#             print("Restaurant details:\n", final_result)
#         else:
#             print("Unexpected result format:", final_result)
#     else:
#         print("Failed to extract restaurant details.")
# else:
#     print("Failed to generate restaurant URL.")
