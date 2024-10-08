# Fast Flow Backend

## Please access the UI code at:
https://github.com/shiv07tiwari/fastflow-ui

## Steps to run

1. Clone the repository
2. Ask me for `firebase cred file`. Add it in the root and its path in `FIRESTORE_CRED_PATH` env variable
3. Set `GEMINI_API_KEY` in the .env file
4. `pip install -r requirements.txt` Install the required packages
5. `playwright install chromium`  This is needed to run web scraping
6. `fastapi run main.py`  This will start the server


## Redis Server

- Start a redis server on your local machine at port 6379
- `brew install redis`
- `redis-server /usr/local/etc/redis.conf`

This will cache the responses from Web Scraping and Gemini API
If redis is not running, the server will still work but it will not cache the responses


## Reddit Scrapping

Set the following env variables
- REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, REDDIT_USERNAME, REDDIT_PASSWORD
- [Go to reddit, create a new app and get the credentials. Set the usage to personal use script](https://www.reddit.com/prefs/apps)
