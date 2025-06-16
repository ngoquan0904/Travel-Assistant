from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
# from ai.context import generate_travel_context_memory
from model import model
import requests
import os
import time 

load_dotenv()
def generate_travel_context_memory(travel_context):
    return f"""I am your travel assistant. I have access to your travel details:
            - Flight from {travel_context['origin']} to {travel_context['destination']}
            - Travel dates: {travel_context['start_date']} to {travel_context['end_date']}
            
            Flight Details: {travel_context['flights']}
            Hotel Details: {travel_context['hotels']}
            """
load_dotenv()

class SerperSearchTool:
    @staticmethod
    def run(query: str) -> list[str]:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": os.getenv("SERPER_API_KEY"),
            "Content-Type": "application/json"
        }
        payload = {"q": query}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if "organic" in data and len(data["organic"]) > 0:
                results = data["organic"][:5]
                return [f"🔹 {item['title']}\n{item['snippet']}" for item in results]
            return ["No search results found."]
        except Exception as e:
            return [f"Search failed: {str(e)}"]
class ResearchAssistant:
    def __init__(self, context):
        # Lưu ngữ cảnh ban đầu
        self.context = context
        self.llm = model

        # Khởi tạo công cụ tìm kiếm DuckDuckGo
        # search = DuckDuckGoSearchRun()

        # Chỉ sử dụng DuckDuckGo làm công cụ
        # self.tools = [
        #     Tool(
        #         name="Search",
        #         func=search.run,
        #         description="Useful for searching information about travel destinations, attractions, local customs, and travel tips"
        #     )
        # ]
        self.tools = [
            Tool(
                name="Search",
                func=SerperSearchTool.run,
                description="Useful for searching information about travel destinations, attractions, local customs, and travel tips"
            )
        ]

        # Bộ nhớ hội thoại
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        self.memory.chat_memory.add_ai_message(
            generate_travel_context_memory(self.context)
        )
        
        # Khởi tạo agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )

        # Lời nhắn hệ thống
        self.system_message = f"""You are a travel research assistant in {self.context['destination']}
        Help users learn about attractions, travel tips, and other travel-related information. 
        Use the Search tool to find general travel information. Always be helpful and informative."""

    def get_response(self, user_input):
        # print(self.context)
        try:
            # Introduce a longer delay to avoid rate limits
            time.sleep(5)  # Wait for 2 seconds before making the request
            response = self.agent.run(input=user_input)
            return response
        except Exception as e:
            return f"I encountered an error while researching. Please try rephrasing your question. Error: {str(e)}"
    class StreamChunk:
        def __init__(self, content):
            self.content = content

    def get_streaming_response(self, user_input):
        try:
            time.sleep(2)
            # Thêm hướng dẫn định dạng markdown vào truy vấn
            markdown_query = (
                f"{user_input}\n"
                "Please format the result as markdown (use bullet points, bold names, etc. if appropriate)."
            )
            # Sử dụng agent để lấy kết quả thay vì chỉ gọi tool trực tiếp
            response = self.agent.run(input=markdown_query)
            # Nếu response là chuỗi dài, chia nhỏ để stream từng phần
            for part in response.split('\n'):
                yield self.StreamChunk(part)
                time.sleep(1.2)
        except Exception as e:
            yield self.StreamChunk(f"❌ Đã xảy ra lỗi khi tìm kiếm: {e}")
        finally:
            print("🔚 Kết thúc quá trình streaming.")
            
    def get_suggested_prompts(self):
        if (self.context['destination'] != "Not specified"):
            return {
                "column1": [
                    f"Find restaurants with high ratings in {self.context['destination']}",
                    f"What are the best seafood restaurants in {self.context['destination']}?",
                    f"Show me restaurants open late night in {self.context['destination']}",
                    f"Find restaurants with outdoor seating in {self.context['destination']}",
                ],
                "column2": [
                    f"What are the most popular local restaurants in {self.context['destination']}",
                    f"Find {self.context['destination']} restaurants that serve vegetarian food",
                    f"What are the best-rated street food spots?",
                    f"Show me restaurants with traditional {self.context['destination']} cuisine",
                ]
            } 
        return {
            "column1": [
                "Find Thai restaurants with high ratings in Bangkok",
                "What are the best seafood restaurants in Phuket?",
                "Show me restaurants open late night in Chiang Mai",
                "Find restaurants with outdoor seating in Thailand",
            ],
            "column2": [
                "What are the most popular local restaurants in Thailand?",
                "Find Thai restaurants that serve vegetarian food",
                "What are the best-rated street food spots?",
                "Show me restaurants with traditional Thai cuisine",
            ]
        }
        
# test_research_assistant.py

# import pprint

# def test_get_response():
#     # Khởi tạo ngữ cảnh mẫu đầy đủ
#     context = {
#         "user_name": "TestUser",
#         "origin": "Hanoi",
#         "destination": "Washington",
#         "start_date": "2024-05-01",
#         "end_date": "2024-05-10",
#         "occupancy": 2,
#         "flights": "Flight VN123 on May 1st, return on May 10th.",
#         "hotels": "",
#         "preferences": {
#             "interests": ["beaches", "culture", "local food"],
#             "budget": "medium"
#         }
#     }

#     assistant = ResearchAssistant(context)
#     user_input = "What are some popular cultural attractions in Viet Nam?"
#     response = assistant.get_streaming_response(user_input)

#     print("\n=== Test Response ===\n")
#     import pprint
#     pprint.pprint(response)


# if __name__ == "__main__":
#     test_get_response()
