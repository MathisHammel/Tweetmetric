#!/usr/bin/env sh

env_file=".env"
src_dir="src/"

if [ -f "${env_file}" ]; then
  set -o allexport
  source "${env_file}"
  set +o allexport 
fi

pkill -f "fetch_loop.py"
pkill -f "viz_server.py"
python -u "${src_dir}/fetch_loop.py" 2>&1 &
python -u "${src_dir}/viz_server.py" 2>&1
echo "Started"
