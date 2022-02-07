#!/bin/bash

if [[ ${MIRROR_PROJECT_HOME} ]]; then
  REPO_PATH="${MIRROR_PROJECT_HOME}/Tweetmetric/"
else
  REPO_PATH="${PROJECT_HOME}/Tweetmetric/"
fi

cd "${REPO_PATH}" && git pull origin "${GIT_BRANCH}" || :
git push github main
git push pgitlab main
exit 0
