import logging
from telegram_bot.bot import MyTelegramBot
from coolq_bot.bot import CooQBot

logging.basicConfig(level=logging.INFO)


class ForwardBot:
    def __init__(self):
        self.cache = None

    def refresh(self):
        coolq_bot.refresh()
        self.cache = coolq_bot.get_cache()

    def id_to_name_cache(self, cache_type):
        return self.cache[cache_type]

    def send_to_qq(self, text):
        coolq_bot.send_to_qq(text)

    def change_qq_chat(self, qq_id, is_group):
        coolq_bot.change_current(qq_id, is_group)

    def send_to_telegram(self, text):
        telegram_bot.send_to_myself(text)

    def get_current_chat(self):
        return coolq_bot.get_cur_info()

    def run(self):
        self.cache = coolq_bot.get_cache()


forward_bot = ForwardBot()
coolq_bot = CooQBot(forward_bot)

forward_bot.run()

telegram_bot = MyTelegramBot(forward_bot)

telegram_bot.run()
coolq_bot.run()

