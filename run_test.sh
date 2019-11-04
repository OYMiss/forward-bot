# 用户设置
tg_telegram_id=404348187
qq_id=1195129533

# 密码设置
tg_group_token=525674017:AAF7HPnA_d-SZbg_Q3BKOF3y5GQ9CkDhcUA
tg_friend_token=531873229:AAH3vEBkpMEtdJgxuYNIWOhO8_ofSaW_n6A

vnc_passwd=fK32lrGf

qq_access_token=Mgep4rV49rM8Jf
qq_secret=kP9yK2lrGxoymmpo

# 代理设置
use_proxy=True # True or False
proxy_url=socks5h://host.docker.internal:1080

ip() {
    docker inspect --format '{{ .NetworkSettings.IPAddress }}' $1
}

cool_bot_ip=172.17.0.2

# 启动 Telegram 机器人
echo init Telegram bot
tg_container_id=$(docker run -d --rm --name forward-test \
            -e TG_TELEGRAM_ID=$tg_telegram_id \
            -e TG_ENABLE_PROXY=$use_proxy \
            -e TG_PROXY_URL=$proxy_url \
            -e TG_GROUP_TOKEN=$tg_group_token \
            -e TG_FRIEND_TOKEN=$tg_friend_token \
            -e QQ_ACCESS_TOKEN=$qq_access_token \
            -e QQ_SECRET=$qq_secret \
            -e QQ_API_ROOT=http://$cool_bot_ip:5700/ \
            -e QQ_POST_HOST=0.0.0.0 \
            -e QQ_POST_PORT=8080 \
            oymiss/forward-bot:beta)

forward_bot_ip=$(ip $tg_container_id)

# 启动 CoolQ
echo start CoolQ bot
qq_container_id=$(docker run -di --rm --name cqhttp-test \
            -v ~/coolq:/home/user/coolq \
            -p 9000:9000  \
            -e FORCE_ENV=true \
            -e COOLQ_ACCOUNT=$qq_id \
            -e CQHTTP_POST_URL=http://$forward_bot_ip:8080 \
            -e CQHTTP_SERVE_DATA_FILES=yes \
            -e CQHTTP_SECRET=$qq_secret \
            -e CQHTTP_ACCESS_TOKEN=$qq_access_token \
            -e CQHTTP_POST_MESSAGE_FORMAT=array \
            -e VNC_PASSWD=$vnc_passwd \
            richardchien/cqhttp:4.12.0)
cool_bot_ip=$(ip $qq_container_id)

echo restart Telegram bot

docker stop $tg_container_id

tg_container_id=$(docker run -d --rm --name forward-test \
            -e TG_TELEGRAM_ID=$tg_telegram_id \
            -e TG_ENABLE_PROXY=$use_proxy \
            -e TG_PROXY_URL=$proxy_url \
            -e TG_GROUP_TOKEN=$tg_group_token \
            -e TG_FRIEND_TOKEN=$tg_friend_token \
            -e QQ_ACCESS_TOKEN=$qq_access_token \
            -e QQ_SECRET=$qq_secret \
            -e QQ_API_ROOT=http://$cool_bot_ip:5700/ \
            -e QQ_POST_HOST=0.0.0.0 \
            -e QQ_POST_PORT=8080 \
            oymiss/forward-bot:beta)
