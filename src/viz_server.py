import collections
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from datetime import datetime
import json
import plotly.express as px
import plotly.graph_objects as go
import redis
import pandas as pd
import pytz
import time

DISPLAY_CHAR_LIMIT = 100
FIELDS_ORDER = ['impression_count', 'retweet_count', 'reply_count', 'like_count', 'quote_count', 'user_profile_clicks', 'url_link_clicks']
TIMEZONE = pytz.timezone('Europe/Paris')

ALIGN_TIME = 6 * 3600  # 6 hours. Time at which all curves meet
CUTOFF_TIME = 2 * 86400 # 2 days. Default time span for the displayed graph

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

    selected_tweet_id = None
    selected_tweet_score = -1
    time_now = int(time.time()) + 1
    for tweet_date, tweet_id, _ in sorted_tweets_most_recent[:100]:
        metrics = redis_cli.hgetall(tweet_id)
        latest_point = max(metrics.keys(), key=int)
        likes = json.loads(metrics[latest_point])[3]
        score = likes / (time_now - tweet_date)
        if score > selected_tweet_score:
            selected_tweet_id = tweet_id
            selected_tweet_score = score

    return html.Div([
        dcc.Graph(id='graph',
            style={'height': '90vh'}),
        dcc.Dropdown(
            id='tweet-selector',
            options=[
                {'label': tweet[2] if len(tweet[2]) < DISPLAY_CHAR_LIMIT else tweet[2][:DISPLAY_CHAR_LIMIT]+'...', 'value': tweet[1]} for tweet in sorted_tweets_most_recent[:500]
            ],
            value=selected_tweet_id  # sorted_tweets_most_recent[0][1]
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
    first_timestamp = None
    last_timestamp = None
    metrics_init = None
    metrics_align = None
    metrics_cutoff = None
    for timestamp in sorted(metrics_raw.keys(), key=int):
        metrics_parsed = json.loads(metrics_raw[timestamp])
        for field, value in zip(FIELDS_ORDER, metrics_parsed):
            metrics[field].append(value)
        metrics['timestamp'].append(datetime.fromtimestamp(int(timestamp), TIMEZONE).isoformat())
        metrics['followers'].append(int(followers_raw.get(timestamp, default_follower_count)))
        
        metrics_vec = dict(zip(FIELDS_ORDER, metrics_parsed))
        metrics_vec.update({'followers': metrics['followers'][-1]})

        if first_timestamp is None:
            first_timestamp = int(timestamp)
            metrics_init = metrics_vec
        if int(timestamp) - first_timestamp < ALIGN_TIME:
            metrics_align = metrics_vec
        if int(timestamp) - first_timestamp < CUTOFF_TIME:
            metrics_cutoff = metrics_vec

        last_timestamp = int(timestamp)
    #df = pd.DataFrame(metrics)
    #fig = px.line(df, x='timestamp', y=['like_count', 'retweet_count']) #, title=tweet_id) 
    
    metrics_scale = {}
    for metric_name in FIELDS_ORDER + ['followers']:
        if metrics_align[metric_name] > metrics_init[metric_name]:
            metrics_scale[metric_name] = (metrics_align[metric_name] - metrics_init[metric_name]) / (metrics_cutoff[metric_name] - metrics_init[metric_name])
    scale_factor = min(metrics_scale.values())
    for metric_name in metrics_scale:
        metrics_scale[metric_name] /= scale_factor


    fig = go.Figure()
    
    col_idx = 0
    for col_name in metrics.keys():
        if col_name == 'timestamp' or len(set(metrics[col_name])) < 2:
            continue

        fig.add_trace(
            go.Scatter(
                x=metrics['timestamp'],
                y=metrics[col_name],
                name=col_name,
                yaxis=f'y{col_idx+1}')
        )

        startval = metrics_init[col_name]
        endval = metrics_cutoff[col_name]
        range_width = metrics_scale.get(col_name, 1) * (endval - startval)
        yaxis_range = [
            startval - 0.05 * range_width,
            startval + 1.05 * range_width
        ]
        if col_idx:
            fig.layout[f'yaxis{col_idx+1}'] = {'overlaying':'y','visible':False, 'range':yaxis_range}
        else:
            fig.layout['yaxis'] = {'range':yaxis_range, 'visible':False}
        
        col_idx += 1
    xaxis_range = [
            datetime.fromtimestamp(int(first_timestamp), TIMEZONE).isoformat(),
            datetime.fromtimestamp(min(int(last_timestamp), int(first_timestamp)+CUTOFF_TIME), TIMEZONE).isoformat()
    ]
    fig.layout['xaxis'] = {'range':xaxis_range} 

    #fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    ssl_context = ('/etc/letsencrypt/live/mathis.h25.io/cert.pem','/etc/letsencrypt/live/mathis.h25.io/privkey.pem')
    app.run_server(debug=True, host='0.0.0.0', ssl_context=ssl_context)
