#!/bin/bash

REPO_PATH="${PROJECT_HOME}/Tweetmetric/"

cd "${REPO_PATH}" && git pull origin "${GIT_BRANCH}" || :
git push github main
git push pgitlab main
exit 0
