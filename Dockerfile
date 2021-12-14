FROM python:3-alpine AS tweet_metric_base

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    WERKZEUG_RUN_MAIN=true \
    REDIS_HOST=tweetmetric-redis \
    REDIS_PORT=6379 \
    DEFAULT_MAX_RESULTS=100 \
    RECENT_TWEET_THRESHOLD=3600 \
    REFRESH_RATE_IF_RECENT_TWEETS=600 \
    REFRESH_RATE_DEFAULT=3600 \
    WATCH_REFRESH_RATE=300

COPY ./src /

RUN apk add --no-cache --virtual .build-deps build-base musl-dev && \
    apk add --no-cache libstdc++ && \
    pip3 install --upgrade pip && \
    pip3 install -r /requirements.txt && \
    apk del .build-deps

FROM tweet_metric_base AS fetch_loop

CMD [ "python3", "-u", "/fetch_loop.py" ]

FROM tweet_metric_base AS viz_server

ENV VIZ_SERVER_HOST=0.0.0.0 \
    VIZ_SERVER_PORT=8080

EXPOSE 8080

CMD [ "python3", "-u", "/viz_server.py" ]
