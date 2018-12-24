# forward-bot

Use telegram to chat with your QQ friends.

![效果](/images/12-24.png)

## 安装

测试平台: macOS Mojave 10.14.2

```bash
sudo ifconfig lo0 alias 172.16.0.100
```

```bash
docker pull richardchien/cqhttp:latest

# 运行 docker 示例
docker run -di --rm --name cqhttp-test \
             -v $(pwd)/coolq:/home/user/coolq \
             -p 9000:9000  \
             -p 5700:5700 \
             -e FORCE_ENV=true \
             -e COOLQ_ACCOUNT=123456 \
             -e CQHTTP_POST_URL=http://172.16.0.100:8080 \
             -e CQHTTP_SERVE_DATA_FILES=yes \
             -e CQHTTP_SECRET=kP9yK2lrGxoymmpo \
             -e CQHTTP_ACCESS_TOKEN=Mgep4rV49rM8Jf \
             -e VNC_PASSWD=fK32lrGf \
             richardchien/cqhttp:latest
```

确保本机 9000 和 5700 没有端口占用。

1. `COOLQ_ACCOUNT` 换为机器人的 QQ 账号
2. `CQHTTP_POST_URL` 这个是 forward-bot 容器的地址

> 调用 `docker inspect --format '{{ .NetworkSettings.IPAddress }}' <id>`，`id` 通过 `docker ps` 查看

3. `CQHTTP_SECRET`，`CQHTTP_ACCESS_TOKEN` CoolQ 的 Secret 和 Token。

```bash
docker pull oymiss/forward-bot:alpha

docker run -d --rm --name forward-test \
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
             forward-bot:alpha
```

## 使用方法

1. /show_contacts 显示所有联系方式。
2. 回复消息会把当前联系人切换到消息发送者。