from playwright.async_api import async_playwright
from langchain_community.document_loaders import YoutubeLoader
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from config.model import model
# Gán API key trực tiếp

class YoutubeSearchScraper:
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def fill_youtube_search(self, title):
        try:
            print("Navigating to Youtube...")
            url = f"https://www.youtube.com/"
            await self.page.goto(url)

            # Update the selector to match the actual search input field
            search_input = await self.page.wait_for_selector(
                'input.ytSearchboxComponentInput', timeout=10000
            )
            await search_input.fill(title)
            await search_input.press("Enter")  # Perform search
            await self.page.wait_for_timeout(5000)  # Wait for results to load

            # Extract links of the first 3 videos
            video_links = []
            video_elements = await self.page.query_selector_all(
                'ytd-video-renderer a#thumbnail'
            )
            for video in video_elements[:3]:  # Get the first 3 videos
                href = await video.get_attribute('href')
                if href:
                    video_links.append(f"https://www.youtube.com{href}")

            print("Extracted video links:", video_links)
            return video_links

        except Exception as e:
            print(f"Error filling youtube search: {str(e)}")
            return None

    async def close(self):
        try:
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
def get_title(user_input):
    prompt = f"""
    You are a travel assistant. Based on the user's input, analyze the context and generate a concise and relevant title 
    that matches the specific topic. If the user asks about places, focus on locations. If the user asks about food, 
    focus on restaurants, dishes, or food-related topics.

    User Input:
    {user_input}

    Provide a clear and descriptive title:
    """
    title = model.invoke(prompt).content
    return title

async def get_youtube_urls(title):
    scraper = YoutubeSearchScraper()
    try:
        await scraper.start()
        urls = await scraper.fill_youtube_search(title)
        return urls
    finally:
        print("Closing youtube browser context...")
        await scraper.close()


def get_content(urls):
    content = []
    for url in urls:
        video_id = url.split("v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        content.append(transcript)
    return " ".join([item['text'] for transcript in content for item in transcript])

def get_response(user_input, content):
    prompt = f"""
    You are a highly knowledgeable and detail-oriented travel review assistant. Your task is to provide a comprehensive and insightful response to the user's question based on the following YouTube content. Ensure your response is well-structured, includes relevant details, and addresses the user's query thoroughly.

    YouTube Content:
    {content}

    User Question:
    {user_input}

    Guidelines for your response:
    - Start with a brief summary of the content relevant to the user's question.
    - Highlight key points, such as specific locations, features, or experiences mentioned in the content.
    - Provide additional context or insights if applicable.
    - Conclude with actionable advice or recommendations if relevant.

    Provide a detailed and helpful response:
    """
    response = model.invoke(prompt).content
    return response

# if __name__ == "__main__":
#     user_input = "Review about the Le Bernardin restaurant"
#     title = get_title(user_input)
#     urls = asyncio.run(get_youtube_urls(title))
#     content = get_content(urls)

#     response = get_response(user_input, content)
#     print(response)
