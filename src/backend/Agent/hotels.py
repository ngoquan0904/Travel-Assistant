from playwright.async_api import async_playwright
from browser_use import Agent, Browser, BrowserConfig
from config.model import model

def hotel_scrape_task(preferences, url):
    return f"""Follow these steps in order:
    Go to {url}
    
    1. Wait for the hotel list to load.
    2. Identify 4 hotel options based on preferences: {preferences}
    3. Extract the following hotel details for each hotel:
        * Hotel name
        * Price per night (include currency)
        * Total price for stay (include currency)
        * Rating
        * Address
        * Amenities (if available)
        * Check-in and check-out dates
    4. Return the extracted details of each hotels.
    """
class HotelSearchScraper:
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def fill_hotel_search(self, location, check_in, check_out):
        try:
            print("Navigating to Google Travel Hotels...")
            url = f"https://www.google.com/travel/search?q={location}"
            await self.page.goto(url)

            # Waiting for content to load
            await self.page.wait_for_timeout(5000)
            print(self.page.url)
            return self.page.url

        except Exception as e:
            print(f"Error filling hotel search: {str(e)}")
            return None

    async def close(self):
        try:
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

async def scrape_hotels(url, preferences):
    browser = Browser(
        config=BrowserConfig(
            chrome_instance_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        )
    )

    initial_actions = [
        {"open_tab": {"url": url}},
    ]

    agent = Agent(
        task=hotel_scrape_task(preferences, url),
        llm=model,
        initial_actions=initial_actions,
        browser=browser,
    )

    history = await agent.run()
    await browser.close()
    result = history.final_result()
    return result

async def get_hotel_url(location, check_in, check_out):
    scraper = HotelSearchScraper()
    try:
        await scraper.start()
        url = await scraper.fill_hotel_search(location, check_in, check_out)
        return url
    finally:
        print("Closing hotel browser context...")
        await scraper.close()

# import asyncio
# location = "Washington"
# check_in = "2025-05-01"
# check_out = "2025-05-15"
# preferences = {
#     "check_in": check_in,
#     "check_out": check_out,
#     "price_per_night": "under $200",
#     "rating": "4 stars and up",
#     "amenities": ""
# }
# url = asyncio.run(get_hotel_url(location, check_in, check_out))
# if url:
#     result = asyncio.run(scrape_hotels(url, preferences))
#     print("\n\n\n")
#     print(result)
