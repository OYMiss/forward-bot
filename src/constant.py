# 只有使用 debug_local 的时候才有效
import json

with open('data.json', 'r') as f:
    data = json.load(f)
    print('Read data from data.json!')
    global TELEGRAM_ID, ENABLE_PROXY, PROXY_URL, GROUP_TOKEN, FRIEND_TOKEN
    TELEGRAM_ID = data['TELEGRAM_ID']
    ENABLE_PROXY = data['ENABLE_PROXY']
    PROXY_URL = data['PROXY_URL']
    GROUP_TOKEN = data['GROUP_TOKEN']
    FRIEND_TOKEN = data['FRIEND_TOKEN']

    global ACCESS_TOKEN, SECRET, API_ROOT, POST_HOST, POST_PORT
    ACCESS_TOKEN = data['ACCESS_TOKEN']
    SECRET = data['SECRET']
    API_ROOT = data['API_ROOT']
    POST_HOST = data['POST_HOST']
    POST_PORT = data['POST_PORT']
