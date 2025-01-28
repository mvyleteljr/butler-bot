#!/usr/bin/bash

set -eu
cd ~/butler_bot
git pull
docker compose build
docker compose up restart

