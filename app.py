from flask import Flask, request
import requests
import json
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from waitress import serve

app = Flask(__name__)


API_KEY = "Replace with API_key from AnythingLLM"
WORKSPACE_NAME = "Replace with workspace name"
ACCESS_TOKEN = 'Replace with channel access token'
SECRET = 'Replace with channel secret.'


# 只要改上面就好

base_url = "http://localhost:3001/api/v1/"


@app.route("/", methods=['POST','GET'])
def linebot():
    body = request.get_data(as_text=True)                   # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                        # json 格式化訊息內容
        line_bot_api = LineBotApi(ACCESS_TOKEN)             # 確認 token 是否正確
        handler = WebhookHandler(SECRET)                    # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']     # 加入回傳的 headers
        handler.handle(body, signature)                     # 綁定訊息回傳的相關資訊
        event = json_data.get('events',[{}])[0]
        reply_token = event.get('replyToken')               # 取得回傳訊息的 Token
        message = event.get('message', {})                  
        msg_type = message.get('type')                      # 取得 LINE 收到的訊息類型


        if msg_type=='text':
            username = event.get('source',{}).get('userId')
            user_message = message.get('text')
            try:
                profile = line_bot_api.get_profile(str(username))
                disp_name_str = str(profile)
                disp_name_json = json.loads(disp_name_str)                
                disp_name = disp_name_json['displayName']
                print(f"Disp name:{disp_name}")
            except LineBotApiError as e:
                print(e)
            
            payload = {
                "message": user_message,
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

            print("Checking User..")
            api_call("check_user", headers=headers, user=thread_template)                        
            try:
                print("Chatting...")
                response = api_call("thread_chat", headers=headers, payload=payload, user=thread_template)                        
            except Exception as e:
                app.logger.error("An error occurred: %s", e)
                return "An error occurred, check logs.", 500    
            print(response.status_code)
            response_data = response.json()
            print(response_data)
            reply = response_data["textResponse"]

            
        else:
            reply = 'Input is not text.'
        line_bot_api.reply_message(reply_token,TextSendMessage(reply)) # 回傳訊息
    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略
        
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
            print("Checking function")
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
    # app.run(debug=True)   # Uncomment this to use flask
    serve(app, host="127.0.0.1", port=3535)  #for waitress