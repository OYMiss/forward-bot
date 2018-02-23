from telegram import \
    InlineKeyboardButton, \
    InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, \
    ReplyKeyboardRemove

from telegram.ext import \
    Updater, MessageHandler, Filters,\
    CommandHandler, CallbackQueryHandler

import logging

from constants import CHAT_TYPE_FRIEND, CHAT_TYPE_GROUP, decode_id, makeup_id


def read_config():
    config = open("./telegram_bot.config").read().split()
    token = config[0][len("TG_TOKEN="):]
    telegram_id = int(config[1][len("TG_ID="):])
    is_proxy = True if config[2][len("IS_PROXY="):] == "TRUE" else False

    if is_proxy:
        updater = Updater(token=token, request_kwargs={
            'proxy_url': 'socks5://127.0.0.1:1080/'
        })
    else:
        updater = Updater(token=token)
    return updater, telegram_id


class MyTelegramBot:
    def __init__(self, forward_bot):
        self.updater, self.telegram_id = read_config()
        self.inline_keyboard_cache = dict()
        self.forward_bot = forward_bot

    def delete_message(self, message_id):
        self.updater.bot.delete_message(self.telegram_id, message_id)

    def send_to_myself(self, text, **kwargs):
        logging.info("send to me")
        return self.updater.bot.send_message(chat_id=self.telegram_id, text=text, **kwargs)

    def edit_message(self, text, keyboard, **kwargs):
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.updater.bot.edit_message_text(chat_id=self.telegram_id, text=text, reply_markup=reply_markup, **kwargs)
        # self.updater.bot.edit_message_reply_markup(chat_id=self.telegram_id, reply_markup=reply_markup, **kwargs)

    @staticmethod
    def make_inline_keyboard(name, key):
        return InlineKeyboardButton(name, callback_data=key)

    def send_inline_keyboard(self, text, keyboard):
        logging.info("send inline keyboard")
        reply_markup = InlineKeyboardMarkup(keyboard)
        return self.send_to_myself(text, reply_markup=reply_markup)

    def send_reply_keyboard(self, keyboard):
        # remove the old one
        # self.send_to_myself(reply_markup=ReplyKeyboardRemove())
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        self.send_to_myself(text="更新最近联系人", reply_markup=reply_markup)

    def add_message_handler(self, fun):
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, fun))
        logging.info("add message handler")

    def add_command_handler(self, cmd_name, cmd_fun):
        self.updater.dispatcher.add_handler(CommandHandler(cmd_name, cmd_fun))
        logging.info("add command handler" + cmd_name)

    def handler_command_help(self, bot, update):
        self.send_to_myself("使用 /help 查看帮助。\n"
                            "使用 /current 查看当前聊天。\n使用 /refresh 刷新列表。\n"
                            "使用 /recently 更新快捷键盘\n"
                            "使用 /list_friends 查看所有好友\n使用 /list_groups 查看所有群组")

    def handler_command_recently(self, bot, update):
        self.forward_bot.send_recent_list()

    def handler_command_current(self, bot, update):
        self.send_to_myself(self.forward_bot.get_current_chat())

    def handler_command_refresh(self, bot, update):
        self.init_cache()
        self.send_to_myself("刷新完成")
        logging.info("refresh")

    def handler_command_list_friends(self, bot, update):
        self.send_inline_keyboard("所有好友：\n", self.inline_keyboard_cache[CHAT_TYPE_FRIEND])
        logging.info("list friends")

    def handler_command_list_groups(self, bot, update):
        self.send_inline_keyboard("所有群组：\n", self.inline_keyboard_cache[CHAT_TYPE_GROUP])
        logging.info("list groups")

    def on_button_click(self, bot, update):
        callback_data = update.callback_query.data
        if callback_data[0] == '~':
            self.forward_bot.read_all_unread_message(callback_data[1:])
        else:
            # update.callback_query.edit_message_reply_markup(reply_markup=None)
            # update.callback_query.message.delete()
            self.forward_bot.change_qq_chat_by_id(callback_data)
        logging.info("on button click")

    def handler_custom_keyboard(self, command):
        self.forward_bot.change_qq_chat_by_name(command)

    def on_receive(self, bot, update):
        # check user if OY ?
        if update.message.chat_id != self.telegram_id:
            return
        if len(update.message.text) > 0 and update.message.text[0] == '>':
            self.handler_custom_keyboard(update.message.text)
        else:
            self.forward_bot.send_to_qq(update.message.text)
            logging.info("send to qq")

    def init(self):
        self.init_cache()

        # init handler
        self.add_command_handler("help", self.handler_command_help)
        self.add_command_handler("current", self.handler_command_current)
        self.add_command_handler("recently", self.handler_command_recently)
        self.add_command_handler("refresh", self.handler_command_refresh)
        self.add_command_handler("list_friends", self.handler_command_list_friends)
        self.add_command_handler("list_groups", self.handler_command_list_groups)
        self.add_message_handler(self.on_receive)
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))

    def init_cache(self):
        self.init_inline_keyboard()

    def init_inline_keyboard(self):
        each_row = [list(), list()]
        self.inline_keyboard_cache[CHAT_TYPE_GROUP] = []
        self.inline_keyboard_cache[CHAT_TYPE_FRIEND] = []
        for qq_id, name in self.forward_bot.id_to_name_info().items():
            cache_type = decode_id(qq_id)
            row = each_row[cache_type]
            if len(row) > 0 and len(row) % 2 == 0:
                self.inline_keyboard_cache[cache_type].append(row.copy())
                row.clear()
            row.append(self.make_inline_keyboard(name, qq_id))
        self.inline_keyboard_cache[CHAT_TYPE_GROUP].append(each_row[CHAT_TYPE_GROUP])
        self.inline_keyboard_cache[CHAT_TYPE_FRIEND].append(each_row[CHAT_TYPE_FRIEND])

    def run(self):
        self.init()
        self.updater.start_polling()

