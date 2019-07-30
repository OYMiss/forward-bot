# forward-bot

~~Use telegram to chat with your QQ friends.~~

部分接口已失效，不能用了。

![效果](/images/12-24.png)

## 安装

已测试平台: macOS Mojave 10.14.2，CentOS 7.6.1810

1. 配置网卡，使得 docker 容器能够访问到宿主机的代理（如果 docker 配置了代理或者不需要配置代理跳过即可)

```bash
# 仅适用于macOS
sudo ifconfig lo0 alias 172.16.0.100
```

要想让容器访问代理，把 ss 监听地址设置为 `0.0.0.0`。


2. docker 环境

> 确保 docker 已经安装好。

获取容器的 ip （下面要用到）
`id` 通过 `docker ps` 查看

使用 docker inspect <id> 或者调用 `docker inspect --format '{{ .NetworkSettings.IPAddress }}' <id>`


3. 获取 forward-bot 容器

```bash
docker pull oymiss/forward-bot:alpha
```

```bash
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
             oymiss/forward-bot:alpha
```

测试的时候建议先不加 `-d`，方便调试。

`TG_TELEGRAM_ID` 就是自己的 TELEGRAM_ID（数字的那个，https://t.me/get_id_bot 可以用这个机器人）。

`TG_ENABLE_PROXY` 是否开启代理，使用填 True，不使用填 False。

`TG_PROXY_URL` 如果不使用，也别删。

`TG_GROUP_TOKEN` 接受群组消息的 telegram 的机器人 TOKEN。

`TG_FRIEND_TOKEN` 接受私聊消息的 telegram 的机器人 TOKEN。

`QQ_ACCESS_TOKEN` 对应下一步的 `CQHTTP_ACCESS_TOKEN` 。

`QQ_SECRET` 对应下一步的的 `CQHTTP_SECRET`。

`QQ_API_ROOT` 下一步的 cqhttp 容器的 IP。


3. 获取 cqhttp 容器

```bash
docker pull richardchien/cqhttp:latest
```

```bash
# 运行 docker 示例
docker run -di --rm --name cqhttp-test \
             -v $(pwd)/coolq:/home/user/coolq \
             -p 9000:9000  \
             -p 5700:5700 \
             -e FORCE_ENV=true \
             -e COOLQ_ACCOUNT=123456 \
             -e CQHTTP_POST_URL=http://172.17.0.2:8080 \
             -e CQHTTP_SERVE_DATA_FILES=yes \
             -e CQHTTP_SECRET=kP9yK2lrGxoymmpo \
             -e CQHTTP_ACCESS_TOKEN=Mgep4rV49rM8Jf \
             -e VNC_PASSWD=fK32lrGf \
             richardchien/cqhttp:latest

```

确保本机 9000 和 5700 可用。

`COOLQ_ACCOUNT` QQ 机器人的账号

`CQHTTP_POST_URL` 对应下一步 forward-bot 容器的 IP 地址。

`CQHTTP_SECRET`，`CQHTTP_ACCESS_TOKEN` 为密钥，测试成功后建议修改。

`VNC_PASSWD` noVNC 密码。

开启之后，打开 `http://127.0.0.1:9000/`，登陆 QQ 号码（服务器的话就是公网ip）。

## 使用方法

1. /show_contacts 显示所有联系方式。
2. 回复消息会把当前联系人切换到消息发送者。
