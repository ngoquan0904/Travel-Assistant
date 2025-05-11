from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
import os
from dotenv import load_dotenv
api_key = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=api_key, streaming=True)
def chat_based_on_context(user_input, messages):
    """
    Trả lời user_input dựa trên lịch sử hội thoại messages bằng mô hình Gemini.
    """
    # Chuyển đổi messages đã lưu sang định dạng tương thích với Gemini
    chat_history = []
    for msg in messages:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))

    chat_history.append(HumanMessage(content=user_input))

    response_stream = model.stream(chat_history)
    return response_stream