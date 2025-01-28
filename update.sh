#!/usr/bin/bash

set -eu
cd ~/butler-bot
git pull
docker compose build
docker compose restart

