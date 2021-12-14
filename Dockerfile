FROM python:3-alpine AS api

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    REDIS_HOST=tweetmetric_redis \
    REDIS_PORT=6379 \
    DEFAULT_MAX_RESULTS=100 \
    RECENT_TWEET_THRESHOLD=3600 \
    REFRESH_RATE_IF_RECENT_TWEETS=600 \
    REFRESH_RATE_DEFAULT=3600 \
    WATCH_REFRESH_RATE=300

COPY launch.sh ./src /

RUN chmod +x launch.sh && \
    pip3 install --upgrade pip && \
    pip3 install -r /requirements.txt

CMD ["/launch.sh"]
