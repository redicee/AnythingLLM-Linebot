### Create a new environment

### Activate environment

### Install necessary dependencies

1. pip install Flask [https://pypi.org/project/Flask/]
2. pip install line-bot-sdk [https://pypi.org/project/line-bot-sdk/]

### Create/Register/Download

1. Create/Register Line Official Account [https://manager.line.biz/]
2. Create/Register Line Developer Console [https://developers.line.biz/console/]
3. Download Line Official Account App (possibly required to verify/activate, or there was just a long delay and it just happened to work after i finally decided to try downloading the app and click "link") 
4. ngrok [https://ngrok.com/]
5. Anything LLM [https://anythingllm.com/]

### Get required token/API

Step 1. Create Channel at [https://developers.line.biz/console/]

Step 2. Gather required info.
1. Channel secret - obtain from Settings > Messaging API at [https://manager.line.biz/]
2. Channel Access token - obtain from [https://developers.line.biz/console/] after creating a channel
3. Anything LLM API_key - From Settings > Developer API > Generate New API Key

### Setting up your workspace

Create a workspace in Anything LLM and modify as needed.

### Fill in required info.

Open app.py and fill in the required information
- Channel secret
- Channel access token
- Anything LLM API
- Workspace name

### Starting the servers

1. Flask Server
   - change directory to where the app.py file is placed with cd <b>file_path</b>
   - flask run 
      - can change port with -p <b>port_number</b> (e.g. flask run -p 3000)

2. Ngrok
   - ngrok http <b>port_number</b>
      - ex. ngrok http 3000

### Add webhook link to devloper console.
 
Ngrok should generate a link for your localhost server which you will go to where you got the access token and paste.
** Remember to also turn on Webhook.

