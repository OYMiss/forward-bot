import logging

from constant import PROXY_URL, GROUP_TOKEN, FRIEND_TOKEN, ACCESS_TOKEN, SECRET, API_ROOT

logging.basicConfig(level=logging.INFO)

MESSAGE_TARGET_COOLQ = 0
MESSAGE_TARGET_TELEGRAM_FRIEND = 1
MESSAGE_TARGET_TELEGRAM_GROUP = 2

CONTACT_TYPE_FRIEND = 0
CONTACT_TYPE_GROUP = 1


class Content:
    def __init__(self, type: str, value):
        self.type = type
        self.value = value


class Contact:
    def __init__(self, id: int, name: str, type=CONTACT_TYPE_FRIEND, sender_name=None):
        self.id = id
        self.name = name
        self.type = type
        self.sender_name = sender_name


class Message:
    def __init__(self, target: int, receiver: Contact, content: Content, sender: Contact):
        self.target = target
        self.receiver = receiver
        self.content = content
        self.sender = sender


class Cloud:
    target_map = dict()

    def set_target(self, target_id: int, instance):
        self.target_map[target_id] = instance

    def push_cloud(self, message: Message):
        self.handler_message(message)

    def handler_message(self, message: Message):
        self.target_map[message.target].send_message(message)

    def refresh_coolq(self):
        self.target_map[MESSAGE_TARGET_COOLQ].init_friends()
        self.target_map[MESSAGE_TARGET_COOLQ].init_groups()


def start_forwarding():
    from telegram_bot import TelegramBot, TelegramBotConfig
    from coolq_bot import CoolQBot, CoolQBotConfig

    cloud_instance = Cloud()

    coolq_bot_config = CoolQBotConfig(API_ROOT, SECRET, ACCESS_TOKEN)
    coolq_bot = CoolQBot(cloud_instance, MESSAGE_TARGET_COOLQ, coolq_bot_config)
    friend_map, group_map = coolq_bot.get_contact_map()

    telegram_bot_friend_config = TelegramBotConfig(FRIEND_TOKEN, PROXY_URL)
    TelegramBot(cloud_instance, MESSAGE_TARGET_TELEGRAM_FRIEND,
                telegram_bot_friend_config, friend_map)

    telegram_bot_group_config = TelegramBotConfig(GROUP_TOKEN, PROXY_URL)
    TelegramBot(cloud_instance, MESSAGE_TARGET_TELEGRAM_GROUP,
                telegram_bot_group_config, group_map)


if __name__ == '__main__':
    start_forwarding()
