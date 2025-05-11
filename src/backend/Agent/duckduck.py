from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory
from config.model import model
import time 

def generate_travel_context_memory(travel_context):
    return f"""I am your travel assistant. I have access to your travel details:
            - Flight from {travel_context['origin']} to {travel_context['destination']}
            - Travel dates: {travel_context['start_date']} to {travel_context['end_date']}
            
            Flight Details: {travel_context['flights']}
            Hotel Details: {travel_context['hotels']}
            """
class ResearchAssistant:
    def __init__(self, context):
        # Lưu ngữ cảnh ban đầu
        self.context = context
        self.llm = model

        # Khởi tạo công cụ tìm kiếm DuckDuckGo
        search = DuckDuckGoSearchRun()

        # Chỉ sử dụng DuckDuckGo làm công cụ
        self.tools = [
            Tool(
                name="Search",
                func=search.run,
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
            time.sleep(5)
            for chunk in self.agent.stream(input=user_input):
                # Nếu chunk là dict và có key 'content', đó là message
                if hasattr(chunk, 'content') and chunk.content:
                    yield self.StreamChunk(chunk.content)
                elif isinstance(chunk, dict) and 'content' in chunk and chunk['content']:
                    yield self.StreamChunk(chunk['content'])
        except Exception as e:
            yield self.StreamChunk(f"Đã xảy ra lỗi trong quá trình streaming: {e}")
        finally:
            print("Kết thúc quá trình streaming.")
            
    def get_suggested_prompts(self):
        if (self.context['destination'] != "Not specified"):
            return {
                "column1": [
                    f"Find Thai restaurants with high ratings in {self.context['destination']}",
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