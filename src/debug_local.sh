function get_json_value {
    echo $1 > tmp
    python3 read_json.py < tmp
    rm tmp
}

# 用户设置
qq_id=$(get_json_value QQ_ID)
vnc_passwd=$(get_json_value VNC_PASSWD)

# 密码设置
qq_access_token=$(get_json_value ACCESS_TOKEN)
qq_secret=$(get_json_value SECRET)

# 网络设置
localhost=$(get_json_value LOCALHOST)

echo QQ_ID=$qq_id
echo VNC_PASSWD=$vnc_passwd
echo QQ_ACCESS_TOKEN=$qq_access_token
echo QQ_SECRET=$qq_secret
echo LOCALHOST=$localhost

# 启动 CoolQ
echo 启动 CoolQ 机器人
docker run -di --rm --name cqhttp-test \
            -v ~/coolq:/home/user/coolq \
            -p 9000:9000  \
            -p 5700:5700  \
            -e FORCE_ENV=true \
            -e COOLQ_ACCOUNT=$qq_id \
            -e CQHTTP_POST_URL=http://$localhost \
            -e CQHTTP_SERVE_DATA_FILES=yes \
            -e CQHTTP_SECRET=$qq_secret \
            -e CQHTTP_ACCESS_TOKEN=$qq_access_token \
            -e VNC_PASSWD=$vnc_passwd \
            richardchien/cqhttp:4.12.0


echo 启动 Telegram 机器人
python3 main.py


