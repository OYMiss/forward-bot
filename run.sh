#!/usr/bin/env bash
sudo ifconfig lo0 alias 172.16.0.100

docker run -di --rm --name cqhttp-test \
             -v $(pwd)/coolq:/home/user/coolq \
             -p 9000:9000  \
             -p 5700:5700 \
             -e FORCE_ENV=true \
             -e COOLQ_ACCOUNT=2991234664 \
             -e CQHTTP_POST_URL=http://172.17.0.2:8080 \
             -e CQHTTP_SERVE_DATA_FILES=yes \
             -e CQHTTP_SECRET=kP9yK2lrGxoymmpo \
             -e CQHTTP_ACCESS_TOKEN=Mgep4rV49rM8Jf \
             -e VNC_PASSWD=fK32lrGf \
             richardchien/cqhttp:latest

docker run --rm --name forward-test \
             -e TG_TELEGRAM_ID=404348187 \
             -e TG_ENABLE_PROXY=True \
             -e TG_PROXY_URL=socks5h://172.16.0.100:1086/ \
             -e TG_GROUP_TOKEN=525674017:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA \
             -e TG_FRIEND_TOKEN=531873229:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA \
             -e QQ_ACCESS_TOKEN=Mgep4rV49rM8Jf \
             -e QQ_SECRET=kP9yK2lrGxoymmpo \
             -e QQ_API_ROOT=http://172.17.0.3:5700/ \
             -e QQ_POST_HOST=0.0.0.0 \
             -e QQ_POST_PORT=8080 \
             oymiss/forward-bot:alpha