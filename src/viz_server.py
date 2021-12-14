import os
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from datetime import datetime
import json
import plotly.express as px
import plotly.graph_objects as go
import redis
import pytz

DISPLAY_CHAR_LIMIT = 100
FIELDS_ORDER = ['impression_count', 'retweet_count', 'reply_count', 'like_count', 'quote_count', 'user_profile_clicks', 'url_link_clicks']
TIMEZONE = pytz.timezone('Europe/Paris')

redis_cli = redis.Redis(host='localhost', port=6379, db=0)

app = dash.Dash(__name__)

def render_layout():
    tweet_contents = {}
    tweet_text = redis_cli.hgetall('tweet_text')
    tweet_creationdate = redis_cli.hgetall('creation_date')
    sorted_tweets_most_recent = []
    for tweet_id in tweet_text:
        date = int(tweet_creationdate[tweet_id])
        sorted_tweets_most_recent.append((date, tweet_id.decode(), tweet_text[tweet_id].decode()))
    sorted_tweets_most_recent.sort(reverse=True)

    return html.Div([
        dcc.Graph(id='graph',
            style={'height': '90vh'}),
        dcc.Dropdown(
            id='tweet-selector',
            options=[
                {'label': tweet[2] if len(tweet[2]) < DISPLAY_CHAR_LIMIT else tweet[2][:DISPLAY_CHAR_LIMIT]+'...', 'value': tweet[1]} for tweet in sorted_tweets_most_recent[:100]
            ],
            value=sorted_tweets_most_recent[0][1]
        )
    ])

app.layout = render_layout

@app.callback(
    Output('graph', 'figure'),
    Input('tweet-selector', 'value'))
def update_figure(tweet_id):
    metrics = {field : [] for field in FIELDS_ORDER}
    metrics['timestamp'] = []
    metrics['followers'] = []
    metrics_raw = redis_cli.hgetall(tweet_id) # {'123456789' : '[13, 0, 4, 2, 5, -1, -1]'}
    followers_raw = redis_cli.hgetall('followers')
    default_follower_count = min(map(int, followers_raw.values()))
    for timestamp in sorted(metrics_raw.keys(), key=int):
        for field, value in zip(FIELDS_ORDER, json.loads(metrics_raw[timestamp])):
            metrics[field].append(value)
        metrics['timestamp'].append(datetime.fromtimestamp(int(timestamp), TIMEZONE).isoformat())
        metrics['followers'].append(int(followers_raw.get(timestamp, default_follower_count)))
    
    fig = go.Figure()
    
    col_idx = 0
    for col_name in metrics.keys():
        if col_name == 'timestamp' or len(set(metrics[col_name])) < 2:
            continue
        fig.add_trace(go.Scatter(
            x=metrics['timestamp'],
            y=metrics[col_name],
            name=col_name,
            yaxis=f'y{col_idx+1}'
        ))
        if col_idx:
            fig.layout[f'yaxis{col_idx+1}'] = {'overlaying':'y','visible':False}
        
        col_idx += 1
    
    fig.layout[f'yaxis'] = {'visible':False}

    #fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':

    app.run_server(debug=True, host=os.environ['VIZ_SERVER_HOST'], port = int(os.environ['VIZ_SERVER_PORT']))
