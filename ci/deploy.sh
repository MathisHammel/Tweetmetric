#!/bin/bash

REPO_PATH="${PROJECT_HOME}/Tweetmetric/"

cd "${REPO_PATH}" && git pull origin "${GIT_BRANCH}" || :
echo "API_KEY=\"${API_KEY}\"" > .env
echo "API_KEY_SECRET=\"${API_KEY_SECRET}\"" > .env
echo "USER_ACCESS_TOKEN=\"${USER_ACCESS_TOKEN}\"" > .env
echo "USER_ACCESS_TOKEN_SECRET=\"${USER_ACCESS_TOKEN_SECRET}\"" > .env
echo "BEARER_TOKEN=\"${BEARER_TOKEN_P1}%${BEARER_TOKEN_P2}%${BEARER_TOKEN_P3}\"" > .env
echo "REDIS_HOST=\"tweetmetric-redis\"" >> .env

docker-compose up -d --force-recreate
