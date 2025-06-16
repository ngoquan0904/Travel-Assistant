import streamlit as st 
import asyncio
from datetime import datetime
from travel_summary import TravelSummary
from api_client import TravelAPIClient
from duckduck import ResearchAssistant
from user_input_summary import get_flight_details, get_hotel_details
from constant import *
from model import chat_based_on_context
import re
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', 'Arial', sans-serif !important;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)
def format_date(date_str):
    if isinstance(date_str, datetime):
        return date_str.strftime("%B %d, %Y")
    return date_str

# ResearchAssistant._initialize_vector_store()

def initialize_session_state():
    """Initialize all session state variables"""
    if 'search_requirements' not in st.session_state:
        st.session_state.search_requirements = ""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'research_assistant' not in st.session_state:
        st.session_state.research_assistant = None
    if 'research_messages' not in st.session_state:
        st.session_state.research_messages = []
    if 'ytb_rv_messages' not in st.session_state:
        st.session_state.ytb_rv_messages = []
    if 'parsed_data' not in st.session_state:
        st.session_state.parsed_data = None
    if 'progress_bar' not in st.session_state:
        st.session_state.progress_bar =  None
    if 'travel_context' not in st.session_state:
        st.session_state.travel_context =  {
            "origin": "Not specified",
            "destination":"Not specified",
            "start_date":"Not specified",
            "end_date": "Not specified",
            "flights": "Not specified",
            "hotels": "Not specified"
        }

def display_parsed_flight_details(parsed_data):
    with st.expander("Parsed Travel Details", expanded=True):
        if not parsed_data:
            st.error("Failed to parse travel details.")
            st.stop()
        st.subheader("✈️ Flight Info Extracted:")
        st.json(parsed_data.model_dump())
        if not ((parsed_data.origin and parsed_data.destination)):
            st.error(MISSING_AIRPORTS_ERROR)
            st.stop()
            
        if not ((parsed_data.start_date and parsed_data.end_date)):
            st.error(MISSING_DATES_ERROR)
            st.stop()

def search_flight_options(parsed_data, requirements, progress_container):
    with progress_container.status("✨ Finding the best options for you...", state="running", expanded=True):
        my_bar = st.progress(0)
        try:
            st.write("✈️ Finding available flights for your dates..")
            preferences = {
                "budget": parsed_data.budget,
                "class": parsed_data.ticket_class,
                "airlines": [parsed_data.airline] if parsed_data.airline else []
            }
            try:
                flight_response = api_client.search_flights(
                    parsed_data.origin,
                    parsed_data.destination,
                    parsed_data.start_date,
                    parsed_data.end_date,
                    preferences
                )
            except Exception as e:
                st.error(f"An error occurred while searching for flights: {str(e)}")
                return False
            my_bar.progress(0.2)
            if flight_response.status_code != 200:
                st.error(SEARCH_FAILED)
                return False

            st.write(" - ✈️ Analyzing flight options and prices...")
            flight_task_id = flight_response.json().get("task_id")
            flight_results = api_client.poll_task_status(flight_task_id, "flight", st)
            if not flight_results:
                st.error(SEARCH_INCOMPLETE)
                return False

            my_bar.progress(0.4)
            st.write(" - ✨ Putting together your perfect flight...")
            summary = travel_summary.get_flight_summary(
                flight_results,
                requirements,
                origin=parsed_data.origin,
                destination=parsed_data.destination,
                start_date=parsed_data.start_date,
                end_date=parsed_data.end_date,
            )
            st.markdown(summary)
            my_bar.progress(0.8)
            st.success(SEARCH_COMPLETED)
            st.session_state.travel_context.update({
                "origin": parsed_data.origin,
                "destination": parsed_data.destination,
                "start_date": parsed_data.start_date,
                "end_date": parsed_data.end_date,
                "flights": flight_results,
            })
            st.session_state.switch_to_result = True
            return True
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return False

def render_flight_search_tab():
    st.header("Tell us about your trip")

    requirements = st.text_area(
        "Describe your travel plans in natural language",
        height=200,
        help=TRAVEL_DESCRIPTION_HELP,
        placeholder=FLIGHT_DESCRIPTION_PLACEHOLDER,
        key="flight_requirements"
    )
    if st.button("Search", key="flight_search_button"):
        if not requirements:
            st.warning(MISSING_DESCRIPTION_ERROR)
            st.stop()
        
        parsed_data = get_flight_details(requirements)
        st.session_state.parsed_data = parsed_data
        display_parsed_flight_details(parsed_data)
        progress_container = st.container()
        search_flight_options(parsed_data, requirements, progress_container)

def display_parsed_hotel_details(parsed_data):
    with st.expander("Parsed Travel Details", expanded=True):
        if not parsed_data:
            st.error("Failed to parse travel details.")
            st.stop()
        st.subheader("🏨 Hotel Info Extracted:")
        st.json(parsed_data.model_dump())
        if not ((parsed_data.location)):
            st.error(MISSING_LOCATION_ERROR)
            st.stop()

def search_hotel_options(parsed_data, requirements, progress_container):
    with progress_container.status("✨ Finding the best options for you...",state="running", expanded=True):
        my_bar = st.progress(0)
        try:
            st.write("🏨 Finding available hotel..")
            preferences = {
                "check_in": parsed_data.check_in,
                "check_out": parsed_data.check_out,
                "rating": parsed_data.rating,
                "price": parsed_data.price_per_night,
                "amenities": parsed_data.amenities
            }
            try:

                hotel_response = api_client.search_hotels(
                    parsed_data.location,
                    parsed_data.check_in,
                    parsed_data.check_out,
                    preferences
                )
            except Exception as e:
                st.error(f"An error occurred while searching for hotels: {str(e)}")
                return False
            my_bar.progress(0.2)
            if hotel_response.status_code != 200:
                st.error(SEARCH_FAILED)
                return False

            st.write("🏨 Analyzing hotel options and prices...")
            hotel_task_id = hotel_response.json().get("task_id")
            hotel_results = api_client.poll_task_status(hotel_task_id, "hotel", st)
            if not hotel_results:
                st.error(SEARCH_INCOMPLETE)
                return False

            my_bar.progress(0.4)
            summary = travel_summary.get_hotel_summary(
                hotel_results,
                requirements,
                location = parsed_data.location,
                check_in = parsed_data.check_in,
                check_out = parsed_data.check_out,
            )
            st.markdown(summary)
            my_bar.progress(0.8)
            st.success(SEARCH_COMPLETED)
            st.session_state.travel_context.update({
                "destination": parsed_data.location,
                "start_date": parsed_data.check_in,
                "end_date": parsed_data.check_out,
                "hotels": hotel_results,
            })
            st.session_state.switch_to_result = True
            return True
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return False

def render_hotel_search_tab():
    st.header("Tell us about your trip")

    requirements = st.text_area(
        "Describe your travel plans in natural language",
        height=200,
        help=TRAVEL_DESCRIPTION_HELP,
        placeholder=HOTEL_DESCRIPTION_PLACEHOLDER,
        key="hotel_requirements"
    )
    if st.button("Search", key="hotel_search_button"):
        if not requirements:
            st.warning(MISSING_DESCRIPTION_ERROR)
            st.stop()
        
        parsed_data = get_hotel_details(requirements)
        st.session_state.parsed_data = parsed_data
        display_parsed_hotel_details(parsed_data)
        progress_container = st.container()
        search_hotel_options(parsed_data, requirements, progress_container)
def clean_response(text):
    text = re.sub(r'\s*•\s*', '\n- ', text)  
    text = re.sub(r'\.\s*', '.\n', text)     
    text = re.sub(r'\s{2,}', ' ', text)      
    return text.strip()
def format_review_response(text):
    # Tách các mục dựa trên số thứ tự hoặc dấu chấm
    lines = re.split(r'(?<=\d\.)\s+', text)
    formatted = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Đánh dấu tên quán ăn bằng in đậm nếu có
        match = re.match(r"^([\w\s&'’\-\.]+)\.?\s*(\d\.\d)?", line)
        if match:
            name = match.group(1).strip()
            rating = match.group(2)
            if rating:
                formatted.append(f"- **{name}** ⭐️ {rating}")
            else:
                formatted.append(f"- **{name}**")
        else:
            formatted.append(f"- {line}")
    return "\n".join(formatted)
def render_chat_interface(messages, assistant, input_placeholder, message_type="chat"):
    # Tạo container chứa toàn bộ phần chat
    chat_container = st.container()

    with chat_container:
        # Hiển thị toàn bộ message đã có
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Gợi ý nếu chưa có message nào
        if not messages:
            st.markdown("### Suggested Questions:")
            suggested_prompts = assistant.get_suggested_prompts()
            cols = st.columns(2)
            with cols[0]:
                for prompt in suggested_prompts["column1"]:
                    st.markdown(f"- {prompt}")
            with cols[1]:
                for prompt in suggested_prompts["column2"]:
                    st.markdown(f"- {prompt}")

    # Ô nhập liệu LUÔN ở cuối
    user_input = st.chat_input(input_placeholder)

    if user_input:
        # Lưu và hiển thị tin nhắn người dùng
        messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        # Lấy phản hồi từ AI
        # response = assistant.get_response(user_input)
        # messages.append({"role": "assistant", "content": response})
        # with chat_container:
        #     with st.chat_message("assistant"):
        #         st.markdown(response)
        # Lấy và hiển thị phản hồi từ AI dưới dạng streaming
        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                for chunk in assistant.get_streaming_response(user_input):
                    full_response += chunk.content + "\n"  # thêm dấu xuống dòng
                    # Hoặc có thể wrap trong <div> giữ nguyên format
                    message_placeholder.markdown(f"<div style='white-space: pre-wrap;'>{full_response}</div>", unsafe_allow_html=True)

                message_placeholder.markdown(f"<div style='white-space: pre-wrap;'>{full_response}</div>", unsafe_allow_html=True)
        # Lưu hội thoại
        messages.append({"role": "assistant", "content": full_response})


def render_research_tab():
    st.header("Travel Research Assistant")
    st.write("Travel context", st.session_state.get("travel_context", "No context found"))

    # Kiểm tra và khởi tạo ResearchAssistant nếu chưa tồn tại
    if 'research_assistant' not in st.session_state or st.session_state.research_assistant is None:
        if isinstance(st.session_state.get("travel_context"), dict):
            st.session_state.research_assistant = ResearchAssistant(context=st.session_state.travel_context)
        else:
            st.error("⚠️ Travel context is not available or invalid.")
            return

    # Sử dụng đối tượng ResearchAssistant từ session_state
    render_chat_interface(
        st.session_state.research_messages,
        st.session_state.research_assistant,
        "Ask about your destination",
        "research"
    )
def search_youtube_review(user_input, progress_container):
    with st.spinner("Fetching YouTube reviews..."):
        my_bar = st.progress(0)
        try:
            try:
                ytb_rv_response = api_client.search_youtube(
                    user_input
                )
            except Exception as e:
                st.error(f"An error occurred while searching for youtube: {str(e)}")
                return False
            my_bar.progress(0.2)
            if ytb_rv_response.status_code != 200:
                st.error(SEARCH_FAILED)
                return False

            ytb_rv_task_id = ytb_rv_response.json().get("task_id")
            ytb_rv_results = api_client.poll_task_status(ytb_rv_task_id, "ytb_rv", st)
            if not ytb_rv_results:
                st.error(SEARCH_INCOMPLETE)
                return False

            my_bar.progress(0.4)
            return ytb_rv_results
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return False

def render_ytb_rv_tab():
    # Khởi tạo trạng thái
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "search_done" not in st.session_state:
        st.session_state.search_done = False

    st.title("Travel Chat with YouTube Reviews")

    # Hiển thị lịch sử chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Phần chat_input luôn cố định ở dưới cùng
    user_input = st.chat_input("Share your travel plan or ask a follow-up question")

    if user_input:
        # Lưu và hiển thị tin nhắn người dùng
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        # Xử lý phản hồi từ assistant (streaming)
        with chat_container:
            with st.chat_message("assistant"):
                response_area = st.empty()
                full_response = ""
                if not st.session_state.search_done:
                    # Giả định search_youtube_review cũng trả về string (có thể cần điều chỉnh nếu nó phức tạp hơn)
                    response = search_youtube_review(user_input, st.container()) # Pass an empty container for now
                    st.session_state.search_done = True
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    response_area.markdown(response)
                else:
                    response_stream = chat_based_on_context(user_input, st.session_state.messages)
                    for chunk in response_stream:
                        if chunk and hasattr(chunk, 'content'):
                            full_response += chunk.content
                            response_area.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    global api_client, travel_summary
    api_client = TravelAPIClient()
    travel_summary = TravelSummary()

    initialize_session_state()
    
    st.title("AI Travel Assistant 🧳")
    flight_tab, hotel_tab, research_tab, ytb_rv_tab = st.tabs(["Flight", "Hotel", "Research Assistant", "Youtube Review"])
    with flight_tab:
        render_flight_search_tab()
    with hotel_tab:
        render_hotel_search_tab()
    with research_tab:
        render_research_tab()
    with ytb_rv_tab:
        render_ytb_rv_tab()
    # Handle tab switching after search
    if hasattr(st.session_state, 'switch_to_results') and st.session_state.switch_to_results:
        st.session_state.switch_to_results = False
        # results_tab._active = True

if __name__ == "__main__":
    main()   