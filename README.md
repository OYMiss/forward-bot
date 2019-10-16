# forward-bot

Use telegram to chat with your QQ friends.

![效果](/images/12-24.png)

## 预先准备

1. 找 `@BotFather` 申请两个机器人，一个用来接收私聊消息一个用来接收群消息，并获取他们的 API Token。
2. 利用这个机器人[@userinfobot](https://telegram.me/userinfobot) 获取自己的 Telegram 的 ID。

## 安装

### 拉取镜像

```bash
docker pull oymiss/forward-bot:beta
docker pull richardchien/cqhttp:4.12.0
```

### 运行

```bash
# 方便测试的版本（建议先使用这个）。
wget https://raw.githubusercontent.com/OYMiss/forward-bot/master/run_test.sh

# 服务器版本。
wget https://raw.githubusercontent.com/OYMiss/forward-bot/master/run.sh
```

然后将 `run.sh` 或 `run_test.sh` 里面的
`tg_telegram_id`、`qq_id`、`tg_group_token`、`tg_friend_token` 修改为自己的。

> 按照需求修改代理设置和各种密码，网络设置默认。

```bash
# 运行
chmod +x run_test.sh && ./run_test.sh
```

然后使用打开 `http://your_ip:9000/`，输入 `run.sh` 或 `run_test.sh` 中的 vnc_passwd 进行登陆。

## 已知问题

1. 不支持图片和表情。
2. 联系人超过 100 左右时，用 `/list` 无法显示所有。

## 使用方法

1. `/list` 显示所有联系方式，`/current` 显示当前会话。
2. 回复消息会把当前联系人切换到消息发送者。
