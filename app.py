from flask import Flask, request, abort
import requests
import json
from waitress import serve

from linebot.v3 import WebhookParser
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
app = Flask(__name__)


API_KEY = "Replace with API_key from AnythingLLM"
WORKSPACE_NAME = "Replace with workspace name"
ACCESS_TOKEN = 'Replace with channel access token'
SECRET = 'Replace with channel secret.'


# 只要改上面就好

base_url = "http://localhost:3001/api/v1/"

configuration = Configuration(access_token = ACCESS_TOKEN)
handler = WebhookParser(SECRET)

@app.route("/", methods=['POST','GET'])
def linebot():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)

    try:
        try:
            signature = request.headers['X-Line-Signature']    
            events = handler.parse(body, signature)        
        except InvalidSignatureError:
            abort(400)

        body_event = json_data.get('events',[{}])[0]
        username = body_event.get('source',{}).get('userId')
        
        for event in events:
            if not isinstance(event, MessageEvent):
                continue
            if not isinstance(event.message, TextMessageContent):
                continue
            with ApiClient(configuration) as api_client:
                msg_type = event.message.type  
                line_bot_api = MessagingApi(api_client)
                try:
                    profile = line_bot_api.get_profile(username)
                    try:
                        disp_name = profile.display_name
                    except:
                        print("Failed to get display name")
                except:
                    print("Failed to get profile")
                if msg_type=='text':
                    message = event.message
                    print(f'{disp_name} asked the question "{message.text}"')
                    payload = {
                        "message": message.text,
                        "mode": "chat",
                        "attachments": []
                    }
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    }           
                    thread_template = {
                        "name": disp_name,
                        "slug": username,
                    } 
                    api_call("check_user", headers=headers, user=thread_template)                        
                    try:
                        print("Generating reply...")
                        response = api_call("thread_chat", headers=headers, payload=payload, user=thread_template)                        
                    except Exception as e:
                        app.logger.error("An error occurred: %s", e)
                        return "An error occurred, check logs.", 500
                
                    response_data = response.json()
                    reply = response_data["textResponse"]
                    line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=reply)]
                        )
                    )
                    print("Reply sent.")
                else:
                    print('Not Text.')        
    except:
        print("Exception.")                                         
    return 'OK'                                                      
        

def api_call(METHOD, headers=None, payload=None, user=None):
    
    API_ENDPOINTS = {
    "get_threads": f"workspaace/{WORKSPACE_NAME}",
    "thread_chat": f"workspace/{WORKSPACE_NAME}/thread/{user['slug']}/chat",
    "create_thread": f"workspace/{WORKSPACE_NAME}/thread/new",
    "check_user": f"workspace/{WORKSPACE_NAME}",
    }

    try:
        url = base_url + API_ENDPOINTS.get(METHOD)
        if METHOD == "create_thread":
            response = requests.post(url, json=user, headers=headers)
        elif METHOD == "thread_chat":
            response = requests.post(url, json=payload, headers=headers)
        elif METHOD == "check_user":
            print("Checking User..")
            response = requests.get(url, headers=headers)
            check_user_threads(response.json(), user, headers)
        else:
            raise ValueError(f"Unknown API method: {METHOD}")

        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        app.logger.error(f"API call error for {METHOD}: {e}")
        raise
    
def check_user_threads(response_data, user, headers):
    """Check if user thread exists and create one if not."""
    threads = response_data.get('workspace', [{}])[0].get('threads', [])
    if not any(thread['slug'] == user['slug'] for thread in threads):
        app.logger.info(f"User thread not found. Creating a new thread for {user['name']}.")
        api_call("create_thread", headers=headers, user=user)

    

if __name__ == "__main__":
    print("Server starting. Default port is 3535")
    # app.run(debug=True)   # Uncomment this to use flask
    serve(app, host="127.0.0.1", port=3535)  #for waitress
    