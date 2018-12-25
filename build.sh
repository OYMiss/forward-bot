#!/usr/bin/env bash
git clone https://github.com/OYMiss/forward-bot.git
cd forward-bot
docker build -t forward-bot:alpha .
docker tag forward-bot:alpha oymiss/forward-bot:alpha
docker push oymiss/forward-bot:alpha
