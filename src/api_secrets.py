import os

API_KEY = os.environ['API_KEY']
API_KEY_SECRET = os.environ['API_KEY_SECRET']
USER_ACCESS_TOKEN = os.environ['USER_ACCESS_TOKEN']
USER_ACCESS_TOKEN_SECRET = os.environ['USER_ACCESS_TOKEN_SECRET']
BEARER_TOKEN = os.environ['BEARER_TOKEN']

if 'YOUR TOKEN HERE' in (BEARER_TOKEN, API_KEY, API_KEY_SECRET, USER_ACCESS_TOKEN, USER_ACCESS_TOKEN_SECRET):
    raise ValueError('Please request your Twitter API tokens on developer.twitter.com and place them in .env file. More info in README.md.')
