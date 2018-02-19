from telegram import \
    InlineKeyboardButton, \
    InlineKeyboardMarkup

from telegram.ext import \
    Updater, MessageHandler, Filters,\
    CommandHandler, CallbackQueryHandler

import logging


class MyTelegramBot:
    def __init__(self, forward_bot):
        config = open("./telegram_bot.config").read().split()
        token = config[0][len("TG_TOKEN="):]
        telegram_id = int(config[1][len("TG_ID="):])
        is_proxy = True if config[2][len("IS_PROXY="):] == "TRUE" else False

        if is_proxy:
            self.updater = Updater(token=token, request_kwargs={
                'proxy_url': 'socks5://127.0.0.1:1080/'
            })
        else:
            self.updater = Updater(token=token)
        self.telegram_id = telegram_id
        self.inline_keyboard_cache = dict()
        self.forward_bot = forward_bot
        self.init_cache()
        self.init()

    def delete_message(self, message_id):
        self.updater.bot.delete_message(self.telegram_id, message_id)

    def send_to_myself(self, text, **kwargs):
        logging.info("send to me")
        return self.updater.bot.send_message(chat_id=self.telegram_id, text=text, **kwargs)

    def edit_message(self, text, keyboard, **kwargs):
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.updater.bot.edit_message_text(chat_id=self.telegram_id, text=text, **kwargs)
        self.updater.bot.edit_message_reply_markup(chat_id=self.telegram_id, reply_markup=reply_markup, **kwargs)

    def make_inline_keyboard(self, name, key):
        return InlineKeyboardButton(name, callback_data=key)

    def markup_inline_keyboard(self, keyboard):
        return InlineKeyboardMarkup(keyboard)

    def send_inline_keyboard(self, text, keyboard):
        logging.info("send inline keyboard")
        reply_markup = InlineKeyboardMarkup(keyboard)
        return self.send_to_myself(text, reply_markup=reply_markup)

    def add_message_handler(self, fun):
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, fun))
        logging.info("add message handler")

    def add_command_handler(self, cmd_name, cmd_fun):
        self.updater.dispatcher.add_handler(CommandHandler(cmd_name, cmd_fun))
        logging.info("add command handler" + cmd_name)

    def handler_command_help(self, bot, update):
        self.send_to_myself("使用 /help 查看帮助。\n"
                            "使用 /current 查看当前聊天。\n使用 /refresh 刷新列表。\n"
                            "使用 /list_friends 查看所有好友\n使用 /list_groups 查看所有群组")

    def handler_command_current(self, bot, update):
        self.send_to_myself(self.forward_bot.get_current_chat())

    def handler_command_refresh(self, bot, update):
        self.init_cache()
        self.send_to_myself("刷新完成")
        logging.info("refresh")

    def handler_command_list_friends(self, bot, update):
        self.send_inline_keyboard("所有好友：\n", self.inline_keyboard_cache["friends"])
        logging.info("list friends")

    def handler_command_list_groups(self, bot, update):
        self.send_inline_keyboard("所有群组：\n", self.inline_keyboard_cache["groups"])
        logging.info("list groups")

    def on_button_click(self, bot, update):
        query = update.callback_query
        if query.data[0] == '~':
            self.forward_bot.send_unread_message(query.data[1:])
        else:
            qq_id, is_group = int(query.data[1:]), query.data[0] == '#'
            name = self.forward_bot.id_to_name_cache("groups" if is_group else "friends").get(qq_id)
            self.send_to_myself("聊天变化为 -> " + name)
            self.forward_bot.change_qq_chat(qq_id, is_group)
            logging.info("on button click")

    def on_receive(self, bot, update):
        # check user if OY ?
        if update.message.chat_id != self.telegram_id:
            return
        self.forward_bot.send_to_qq(update.message.text)
        logging.info("send to qq")

    def init(self):
        # init handler
        self.add_command_handler("help", self.handler_command_help)
        self.add_command_handler("current", self.handler_command_current)
        self.add_command_handler("refresh", self.handler_command_refresh)
        self.add_command_handler("list_friends", self.handler_command_list_friends)
        self.add_command_handler("list_groups", self.handler_command_list_groups)
        self.add_message_handler(self.on_receive)
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))

    def init_cache(self):
        self.init_inline_keyboard("friends", prefix="@")
        self.init_inline_keyboard("groups", prefix="#")

    def init_inline_keyboard(self, cache_type, prefix):
        each_row = []
        self.inline_keyboard_cache[cache_type] = []
        for qq_id, name in self.forward_bot.id_to_name_cache(cache_type).items():
            if len(each_row) > 0 and len(each_row) % 2 == 0:
                self.inline_keyboard_cache[cache_type].append(each_row.copy())
                each_row.clear()
            each_row.append(InlineKeyboardButton(name, callback_data=prefix + str(qq_id)))
        self.inline_keyboard_cache[cache_type].append(each_row)

    def run(self):
        self.updater.start_polling()

