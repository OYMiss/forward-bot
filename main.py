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
        self.map_name_to_id = dict()
        # qq_id of recent contact eg:#123 @432
        self.recent_contact = list()

    def add_to_recent(self, qq_id):
        # i think it can be optimized.
        # current time complexity O(n)
        self.recent_contact.append(qq_id)
        if self.recent_contact.count(qq_id) > 1:
            self.recent_contact.remove(qq_id)
        if len(self.recent_contact) > 9:
            del self.recent_contact[0]

    def send_recent_list(self):
        ans = [[]]
        i = 0
        for qq_id in reversed(self.recent_contact):
            name = "> " + self.coolq_bot.info["id_name"][qq_id]
            self.map_name_to_id[name] = qq_id
            ans[i].append(name)
            if len(ans[i]) == 3:
                i += 1
        self.telegram_bot.send_reply_keyboard(ans)

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
        self.add_to_recent(self.coolq_bot.info["cur_id"])
        self.coolq_bot.send_to_qq(text)

    def change_qq_chat_by_id(self, qq_id):
        name = self.get_name_by_id(qq_id)
        self.telegram_bot.send_to_myself("聊天变化为 -> " + name)
        self.coolq_bot.change_current(qq_id)

    def change_qq_chat_by_name(self, command):
        self.change_qq_chat_by_id(self.map_name_to_id[command])

    def send_to_telegram(self, text, qq_id, tail=""):
        self.add_to_recent(qq_id)
        if qq_id == self.coolq_bot.info["cur_id"]:
            self.telegram_bot.send_to_myself(text + tail)
        else:
            self.push_to_unread_queue(text, qq_id, tail)

    def push_to_unread_queue(self, text, qq_id, tail):
        is_first = False
        if self.unread.get(qq_id) is None:
            self.unread[qq_id] = list()
            is_first = True
        if len(self.unread[qq_id]) > 0:
            self.unread[qq_id].pop()
        self.unread[qq_id].append(text)
        self.unread[qq_id].append(tail)
        prefix = "新消息：\n"
        text = prefix + text + tail

        self.update_unread_notification(is_first, qq_id, text)

    def update_unread_notification(self, need_new_msg, qq_id, text):
        num = str(len(self.unread[qq_id]) - 1)
        keyboard = [[MyTelegramBot.make_inline_keyboard("回复", qq_id),
                     MyTelegramBot.make_inline_keyboard("未读：" + num, "~" + qq_id)]]
        if need_new_msg:
            message = self.telegram_bot.send_inline_keyboard(text, keyboard)
            self.message_id[qq_id] = message.message_id
        else:
            self.telegram_bot.edit_message(text, keyboard, message_id=self.message_id[qq_id])

    def read_all_unread_message(self, qq_id):
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
