from flask import Flask, request, jsonify
from Agent.flight import get_flight_url, scrape_flights
from Agent.hotels import get_hotel_url, scrape_hotels
from Agent.youtube import get_title, get_youtube_urls, get_content, get_response
from enum import Enum
from collections import defaultdict
from waitress import serve
import requests
import asyncio
import uuid
import threading

app = Flask(__name__)

# in-memory storage
task_results = defaultdict(dict)
# lock for thread-safe
task_lock = threading.Lock()

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def run_async(coro):
    return loop.run_until_complete(coro)

def update_task_status(task_id, status, data=None, error=None):
    with task_lock:
        if data is not None:
            task_results[task_id].update({
                'status': status,
                'data': data
            })
        elif error is not None:
            task_results[task_id].update({
                'status': status,
                'error': error
            })
        else:
            task_results[task_id]['status'] = status

def process_flight_search(task_id, origin, destination, start_date, end_date, preferences):
    try:
        update_task_status(task_id, TaskStatus.PROCESSING.value)
        print(f"Start date: {start_date}")
        url = run_async(get_flight_url(origin, destination, start_date, end_date))

        if not url:
            raise Exception("Failed to generate flight search URL")
        
        flight_results = run_async(scrape_flights(url, preferences))

        update_task_status(
            task_id, 
            TaskStatus.COMPLETED.value,
            data=flight_results
        )
    except Exception as e:
        print(f"Error in flight search task: {str(e)}")
        update_task_status(
            task_id,
            TaskStatus.FAILED.value,
            error=str(e)
        )
    
def process_hotel_search(task_id, location, check_in, check_out, preferences):
    try: 
        update_task_status(task_id, TaskStatus.PROCESSING.value)

        url = run_async(get_hotel_url(location, check_in, check_out))

        if not url:
            raise Exception("Failed to generate hotel search URL")

        hotel_results = run_async(scrape_hotels(url, preferences))

        update_task_status(
            task_id,
            TaskStatus.COMPLETED.value,
            data = hotel_results
        )
    except Exception as e:
        print(f"Error in hotel search task: {str(e)}")
        update_task_status(
            task_id,
            TaskStatus.FAILED.value,
            error=str(e)
        )
def process_youtube_search(task_id, user_input):
    try: 
        update_task_status(task_id, TaskStatus.PROCESSING.value)
        title = get_title(user_input)
        urls = asyncio.run(get_youtube_urls(title))

        if not urls:
            raise Exception("Failed to generate youtube search URL")

        content = get_content(urls)
        response = get_response(user_input, content)
        update_task_status(
            task_id,
            TaskStatus.COMPLETED.value,
            data = response
        )
    except Exception as e:
        print(f"Error in youtube search task: {str(e)}")
        update_task_status(
            task_id,
            TaskStatus.FAILED.value,
            error=str(e)
        )
    
@app.route('/search_flights', methods=["POST"])
def search_flights():
    try:
        # nhận thông tin json từ client(search_flight trong api_client)
        data = request.get_json()

        origin = data.get('origin')
        destination = data.get('destination')
        start_date = data.get('start_date', '').replace(" 0", " ")
        end_date = data.get('end_date', '').replace(" 0", " ")
        preferences = data.get('preferences', {})

        if not all([origin, destination, start_date, end_date]):
            return jsonify({
                'error': 'Missing required parameters. Please provide origin, destination, start_date and end_date'
            }), 400
        
        task_id = str(uuid.uuid4())
        with task_lock:
            task_results[task_id] = {'status': TaskStatus.PENDING.value}
        # tạo luồng mới
        thread = threading.Thread(
            target=process_flight_search,
            args=(task_id, origin, destination, start_date, end_date, preferences),
            daemon=True # daemon thread tự động dừng luồng khi chương trình chính kết thúc
        )
        thread.start()
        return jsonify({
            'task_id': task_id,
            'status': TaskStatus.PENDING.value
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/search_hotels', methods=["POST"])
def search_hotels():
    try:
        data = request.get_json()

        location = data.get('location')
        check_in = data.get('check_in', '').replace(" 0", " ")
        check_out = data.get('check_out', '').replace(" 0", " ")
        preferences = data.get('preferences', {})

        if not all([location, check_in, check_out]):
            return jsonify({
                'error': 'Missing required parameters. Please provide location, check_in and check_out'
            }), 400
        
        task_id = str(uuid.uuid4())
        with task_lock:
            task_results[task_id] = {'status': TaskStatus.PENDING.value}
        # tạo luồng mới
        thread = threading.Thread(
            target=process_hotel_search,
            args=(task_id, location, check_in, check_out, preferences),
            daemon=True # daemon thread tự động dừng luồng khi chương trình chính kết thúc
        )
        thread.start()
        return jsonify({
            'task_id': task_id,
            'status': TaskStatus.PENDING.value
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
@app.route('/search_youtube', methods=["POST"])
def search_youtube():
    try:
        # nhận thông tin json từ client(search_flight trong api_client)
        data = request.get_json()

        user_input = data.get('user_input')

        if not user_input:
            return jsonify({
                'error': 'Missing required parameters. Please provide question.'
            }), 400
        
        task_id = str(uuid.uuid4())
        with task_lock:
            task_results[task_id] = {'status': TaskStatus.PENDING.value}
        # tạo luồng mới
        thread = threading.Thread(
            target=process_youtube_search,
            args=(task_id, user_input),
            daemon=True # daemon thread tự động dừng luồng khi chương trình chính kết thúc
        )
        thread.start()
        return jsonify({
            'task_id': task_id,
            'status': TaskStatus.PENDING.value
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/task_status/<task_id>', methods=['GET'])
def get_status(task_id):
    try:
        with task_lock:
            result = task_results.get(task_id)
        if not result:
            return jsonify({'error': 'Task not found'}), 404
    
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)