from flask import Flask, request
import threading

auth_callback_app = Flask(__name__)
auth_callback_event = threading.Event()
web_app_auth_data = None

@auth_callback_app.route('/auth-callback', methods=['GET'])
def auth_callback():
    # Retrieve the authorization code from the query parameters
    global web_app_auth_data
    web_app_auth_data = request.args
    if web_app_auth_data.get('code'):
        auth_callback_event.set()
    return "<h3>auth-callback</h3>"

def auth_callback_task():
    auth_callback_app.run(port=5001)

def get_auth_callback_url():
    return "http://localhost:5001/auth-callback"
