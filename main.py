from coolq_bot import coolq_bot as qq_bot
from telegram_bot import telegram_bot as tg_bot
import sys

if __name__ == "__main__":
    config = sys.stdin.read().split()
    if not config[0].startswith("TG_TOKEN="):
        print("请输入正确格式")
        print("TG_TOKEN=YOUR TOKEN")
        exit()
    if not config[1].startswith("TG_ID="):
        print("请输入正确格式")
        print("TG_ID=YOUR ID")
        exit()

    tg_bot.run(config[0][len("TG_TOKEN="):], int(config[1][len("TG_ID="):]), True)
    qq_bot.run()
