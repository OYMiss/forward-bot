#!/usr/bin/env bash
git clone https://github.com/OYMiss/forward-bot.git
cd forward-bot
docker build -t oymiss/forward-bot:beta .
docker push oymiss/forward-bot:beta
