#!/bin/bash

BASE_DIR="$(dirname $0)"
REPO_PATH="${BASE_DIR}/.."
IMAGE="${1}"
VERSION="${2}"

tag_and_push() {
  docker tag "comworkio/${2}:latest" "comworkio/${2}:${1}"
  docker push "comworkio/${2}:${1}"
}

cd "${REPO_PATH}" && git pull origin "${GIT_BRANCH}" || :

echo "${DOCKER_ACCESS_TOKEN}" | docker login --username "${DOCKER_USERNAME}" --password-stdin

COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build "${IMAGE}"

tag_and_push "latest" "${IMAGE}"
tag_and_push "${VERSION}" "${IMAGE}"
tag_and_push "${VERSION}-${CI_COMMIT_SHORT_SHA}" "${IMAGE}"

exit 0
