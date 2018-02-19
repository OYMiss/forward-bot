import logging
from telegram_bot.telegram_bot import MyTelegramBot
from coolq_bot.coolq_bot import CooQBot

logging.basicConfig(level=logging.INFO)


class ForwardBot:
    def __init__(self):
        self.cache = None
        self.current = None
        self.unread = dict()
        self.message_id = dict()

    def refresh(self):
        coolq_bot.refresh()
        self.cache = coolq_bot.cache
        self.current = coolq_bot.current

    def id_to_name_cache(self, cache_type):
        return self.cache[cache_type]

    def send_to_qq(self, text):
        coolq_bot.send_to_qq(text)

    def change_qq_chat(self, qq_id, is_group):
        coolq_bot.change_current(qq_id, is_group)

    def send_to_telegram(self, text, qq_id, is_group):
        if qq_id == self.current["id"] and is_group == self.current["is group"]:
            telegram_bot.send_to_myself(text)
        else:
            key = ("#" if is_group else "@") + str(qq_id)
            is_first = False
            if self.unread.get(key) is None:
                self.unread[key] = list()
                is_first = True

            self.unread[key].append(text)
            name = self.cache["groups" if is_group else "friends"][qq_id]
            keyboard = [[telegram_bot.make_inline_keyboard(name, key),
                        telegram_bot.make_inline_keyboard("未读：" + str(len(self.unread[key])), "~" + key)]]

            if is_first:
                message = telegram_bot.send_inline_keyboard(text, keyboard)
                self.message_id[key] = message.message_id
            else:
                telegram_bot.edit_message(text, keyboard, message_id=self.message_id[key])

    def send_unread_message(self, qq_id):
        text = ""
        messages = self.unread[qq_id]
        for m in messages:
            text += m + "\n"

        self.unread[qq_id] = None
        telegram_bot.delete_message(self.message_id[qq_id])
        name = self.cache["groups" if qq_id[0] == '#' else "friends"][int(qq_id[1:])]
        telegram_bot.send_inline_keyboard("以下是未读消息：\n" + text, [[telegram_bot.make_inline_keyboard(name, qq_id)]])

    def get_current_chat(self):
        return coolq_bot.get_cur_info()

    def run(self):
        self.cache = coolq_bot.cache
        self.current = coolq_bot.current


forward_bot = ForwardBot()
coolq_bot = CooQBot(forward_bot)

forward_bot.run()

telegram_bot = MyTelegramBot(forward_bot)

telegram_bot.run()
coolq_bot.run()

