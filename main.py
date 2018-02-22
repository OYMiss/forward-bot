import logging
from telegram_bot.telegram_bot import MyTelegramBot
from coolq_bot.coolq_bot import CoolQBot

logging.basicConfig(level=logging.INFO)


class ForwardBot:
    coolq_bot = None
    telegram_bot = None

    def __init__(self):
        self.unread = dict()
        self.message_id = dict()

    def set_coolq_bot(self, coolq_bot):
        self.coolq_bot = coolq_bot

    def set_telegram_bot(self, telegram_bot):
        self.telegram_bot = telegram_bot

    def refresh(self):
        self.coolq_bot.refresh()

    def get_name_by_id(self, qq_id):
        return self.coolq_bot.info["id_name"][qq_id]

    def id_to_name_info(self):
        return self.coolq_bot.info["id_name"]

    def send_to_qq(self, text):
        self.coolq_bot.send_to_qq(text)

    def change_qq_chat(self, qq_id):
        self.coolq_bot.change_current(qq_id)

    def send_to_telegram(self, text, qq_id, tail=""):
        if qq_id == self.coolq_bot.info["cur_id"]:
            self.telegram_bot.send_to_myself(text + tail)
        else:
            is_first = False
            if self.unread.get(qq_id) is None:
                self.unread[qq_id] = list()
                is_first = True
            if len(self.unread[qq_id]) > 0:
                self.unread[qq_id].pop()
            self.unread[qq_id].append(text)
            self.unread[qq_id].append(tail)
            prefix = "新消息：\n"
            # name = self.coolq_bot.info["id_name"][qq_id]
            num = str(len(self.unread[qq_id]) - 1)
            keyboard = [[MyTelegramBot.make_inline_keyboard("回复", qq_id),
                         MyTelegramBot.make_inline_keyboard("未读：" + num, "~" + qq_id)]]
            text = prefix + text + tail
            if is_first:
                message = self.telegram_bot.send_inline_keyboard(text, keyboard)
                self.message_id[qq_id] = message.message_id
            else:
                self.telegram_bot.edit_message(text, keyboard, message_id=self.message_id[qq_id])

    def push_unread_message(self, qq_id):
        text = ""
        messages = self.unread[qq_id]
        for m in messages:
            text += m + "\n"

        self.unread[qq_id] = None
        self.telegram_bot.delete_message(self.message_id[qq_id])
        # name = self.coolq_bot.info["id_name"][qq_id]
        keyboard = [[MyTelegramBot.make_inline_keyboard("回复消息", qq_id)]]
        self.telegram_bot.send_inline_keyboard("以下是未读消息：\n" + text, keyboard)

    def get_current_chat(self):
        return self.coolq_bot.get_cur_info()


def run():
    forward_bot = ForwardBot()
    telegram_bot = MyTelegramBot(forward_bot)
    coolq_bot = CoolQBot(forward_bot)
    forward_bot.set_coolq_bot(coolq_bot)
    forward_bot.set_telegram_bot(telegram_bot)
    telegram_bot.run()
    coolq_bot.run()


run()
