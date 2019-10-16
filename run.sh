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
use_proxy=False # True or False
# use_proxy=True
# 最好代理也用 docker 开一个服务。运行时要加上 --network botnet --ip 172.18.0.4，然后下面填 172.18.0.4。
# 如果是 macOS，可以执行 sudo ifconfig lo0 alias 172.16.0.100，然后下面填 172.16.0.100。
# host.docker.internal 无效。

proxy_url=socks5h://ip:1080

# 网络设置
bot_net=172.18.0.0/16
forward_bot_ip=172.18.0.2
cool_bot_ip=172.18.0.3

docker network create --subnet=$bot_net botnet

# 启动 Telegram 机器人
echo 启动 Telegram 机器人
docker run -d --rm --network botnet \
            --ip $forward_bot_ip \
            --dns 8.8.8.8 --dns 114.114.114.114 --name forward-test \
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
            oymiss/forward-bot:beta

# 启动 CoolQ
echo 启动 CoolQ 机器人
docker run -di --rm --network botnet \
            --ip $cool_bot_ip \
            --dns 8.8.8.8 --dns 114.114.114.114 --name cqhttp-test \
            -v $(pwd)/coolq:/home/user/coolq \
            -p 9000:9000  \
            -e FORCE_ENV=true \
            -e COOLQ_ACCOUNT=$qq_id \
            -e CQHTTP_POST_URL=http://$forward_bot_ip:8080 \
            -e CQHTTP_SERVE_DATA_FILES=yes \
            -e CQHTTP_SECRET=$qq_secret \
            -e CQHTTP_ACCESS_TOKEN=$qq_access_token \
            -e VNC_PASSWD=$vnc_passwd \
            richardchien/cqhttp:4.12.0



