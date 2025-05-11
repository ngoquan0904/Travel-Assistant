from playwright.async_api import async_playwright
from browser_use import Agent, Browser, BrowserConfig
from config.model import model
from datetime import datetime
import os
def flight_scrape_task(preferences, url):
    return f"""Follow these steps in order:
    Go to {url}
    1. Find and click the 'Search' button on the page

    2. For the outbound flight (first leg of the journey):
        - Identify the best outbound flight based on user preferences: {preferences}
        - Click on this outbound flight to select it
        - Store the outbound flight details including:
            * Departure time and date
            * Arrival time and date
            * Price
            * Number of stops
            * Stop Location and Time
            * Duration
            * Airlines
            * Origin and destination airports

    3. For the return flight (second leg of the journey):
        - After clicking the outbound flight, you'll see return flight options
        - Identify the best return flight based on user preferences: {preferences}
        - Store the return flight details including:
            * Departure time and date
            * Arrival time and date
            * Price
            * Number of stops
            *Stop Location and Time
            * Duration
            * Airlines
            * Origin and destination airports

    4. Create a structured JSON response with both flights:
        {{
            "outbound_flight": {{
                "start_time": "...",
                "end_time": "...",
                "origin": "...",
                "destination": "...",
                "price": "",
                "num_stops": 0,
                "duration": "...",
                "airline": "...",
                "stop_locations": "...",
            }},
            "return_flight": {{
                "start_time": "...",
                "end_time": "...",
                "origin": "...",
                "destination": "...",
                "price": "",
                "num_stops": 0,
                "duration": "...",
                "airline": "...",
                "stop_locations": "...",
            }}
        }}

    5. Important:
        - Make sure to capture BOTH outbound and return flight details
        - Each flight should have its own complete set of details
        - Store the duration in the format "Xh Ym" (e.g., "2h 15m")
    """


class FlightSearchScraper:
    async def start(self, use_bright_data=True):
        self.playwright = await async_playwright().start()

        if use_bright_data:
            self.browser = await self.playwright.chromium.connect(
                os.getenv("BRIGHTDATA_WSS_URL")
            )
        else:
            self.browser = await self.playwright.chromium.launch(
                headless=False,
            )

        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def find_origin_input(self):
        element = await self.page.wait_for_selector(
            'input[aria-label="Where from?"]', timeout=5000
        )
        if element:
            return element

        raise Exception("Could not find origin input field")

    async def fill_and_select_airport(self, input_selector, airport_name):
        try:
            input_element = await self.page.wait_for_selector(input_selector)
            await input_element.press("Control+a")
            await input_element.press("Delete")
            await input_element.type(airport_name, delay=50)
            await self.page.wait_for_selector(
                f'li[role="option"][aria-label*="{airport_name}"]', timeout=3000
            )
            await self.page.wait_for_timeout(500)

            # Try different selectors for the dropdown item
            dropdown_selectors = [
                f'li[role="option"][aria-label*="{airport_name}"]',
                f'li[role="option"] .zsRT0d:text-is("{airport_name}")',
                f'.zsRT0d:has-text("{airport_name}")',
            ]

            for selector in dropdown_selectors:
                try:
                    dropdown_item = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if dropdown_item:
                        await dropdown_item.click()
                        await self.page.wait_for_load_state("networkidle")
                        return True
                except:
                    continue

            raise Exception(f"Could not select airport: {airport_name}")

        except Exception as e:
            print(f"Error filling airport: {str(e)}")
            await self.page.screenshot(path=f"error_{airport_name.lower()}.png")
            return False

    async def fill_flight_search(self, origin, destination, start_date, end_date):
        try:
            print("Navigating to Google Flights...")
            await self.page.goto("https://www.google.com/travel/flights")

            print("Filling in destination...")
            if not await self.fill_and_select_airport(
                'input[aria-label="Where to? "]', destination
            ):
                raise Exception("Failed to set destination airport")

            print("Filling in origin...")
            if not await self.fill_and_select_airport(
                'input[aria-label="Where from?"]', origin
            ):
                raise Exception("Failed to set origin airport")

            print("Filling in dates...")
            # Input departure date
            departure_input = await self.page.wait_for_selector(
                'input[aria-label*="Departure"]', timeout=5000
            )
            await departure_input.click()
            await self.page.wait_for_timeout(1000)

            # Chọn ngày đi
            await self.page.click(f'div[aria-label="{start_date}"]')
            await self.page.wait_for_timeout(500)  # Directly input the departure date
            print(f"Return date filled: {start_date}")
            await self.page.wait_for_timeout(1000)

            # Input return date
            return_input = await self.page.wait_for_selector(
                'input[aria-label*="Return"]', timeout=5000
            )
            # await return_input.click()
            await self.page.wait_for_timeout(1000)

            await self.page.click(f'div[aria-label="{end_date}"]')
            await self.page.wait_for_timeout(500)
            print(f"Return date filled: {end_date}")
            await return_input.press("Enter")
            await self.page.wait_for_timeout(1000)
            
            try:
                # Tìm nút "Done" với selector chi tiết hơn
                    alternative_done_button = await self.page.wait_for_selector(
                        'button.nCP5yc.AjY5Oe.DuMIQc.LQeN7.z18xM.rtW97.Q74FEc.dAwNDc', timeout=3000
                    )
                    if alternative_done_button:
                        await alternative_done_button.click()
                        print("Clicked alternative 'Done' button.")
            except Exception as e:
                print("No 'Done' button found or required. Trying alternative selector...")

                # Thử với selector khác nếu nút không tìm thấy
                try:
                    alternative_done_button = await self.page.wait_for_selector(
                        'button.nCP5yc.AjY5Oe.DuMIQc.LQeN7.z18xM.rtW97.Q74FEc.dAwNDc', timeout=3000
                    )
                    if alternative_done_button:
                        await alternative_done_button.click()
                        print("Clicked alternative 'Done' button.")
                except Exception as e:
                    print("No alternative 'Done' button found or required.")

            print(self.page.url)
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


async def scrape_flights(url, preferences):
    browser = Browser(
        config=BrowserConfig(
            chrome_instance_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        )
    )
    initial_actions = [
        {"open_tab": {"url": url}},
    ]

    agent = Agent(
        task=flight_scrape_task(preferences, url),
        llm=model,
        initial_actions=initial_actions,
        browser=browser,
    )

    # Chạy tác vụ và ghi log
    print("Starting flight scraping task...")
    history = await agent.run()
    print("Task completed. Fetching result...")

    # Đóng trình duyệt và trả về kết quả
    await browser.close()
    result = history.final_result()
    return result


async def get_flight_url(origin, destination, start_date, end_date):
    try:
        scraper = FlightSearchScraper()
        await scraper.start(use_bright_data=False)
        url = await scraper.fill_flight_search(
            origin=origin,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
        )
        return url

    finally:
        print("Closing connection...")
        if "scraper" in locals():
            await scraper.close()

    return None
# import asyncio

# # # Đặt thông tin chuyến bay cần tìm
# origin = "New York"
# destination = "Paris"
# start_date = "Sunday, May 18, 2025"
# end_date = "Sunday, May 25, 2025"
# preferences = {
#     "budget": "",
#     "ticket_class":"economy",
#     "airline": ""
# }

# # # Lấy URL từ Google Flights
# flight_url = asyncio.run(get_flight_url(origin, destination, start_date, end_date))

# if flight_url:
#     print(f"Flight search URL: {flight_url}")
#     # Lấy thông tin chuyến bay
#     result = asyncio.run(scrape_flights(flight_url, preferences))
#     print("Flight Details:", result)
# else:
#     print("Failed to generate flight search URL.")
