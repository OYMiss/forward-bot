from collections import defaultdict

from constant import TELEGRAM_ID, ENABLE_PROXY
from main import *

from telegram import \
    InlineKeyboardButton, \
    InlineKeyboardMarkup

from telegram.ext import \
    Updater, MessageHandler, Filters, \
    CommandHandler, CallbackQueryHandler


def mark_up_message(message: Message):
    if message.receiver.type == CONTACT_TYPE_FRIEND:
        return "「{0}」：{1}".format(message.sender.name, message.content.value)
    else:
        return "「{0}@{1}」：{2}".format(message.sender.name, message.sender.sender_name, message.content.value)


def make_inline_keyboard(name, key):
    return InlineKeyboardButton(name, callback_data=key)


class TelegramBotConfig:
    def __init__(self, token, proxy_url):
        self.token = token
        self.proxy_url = proxy_url

    def create_updater(self):
        if ENABLE_PROXY:
            updater = Updater(token=self.token,
                              request_kwargs={
                                  'proxy_url': self.proxy_url
                              })
        else:
            updater = Updater(token=self.token)
        return updater


class TelegramBot:
    def __init__(self, cloud: Cloud, target_key: int, config: TelegramBotConfig, contact_map: dict):
        self.current_receiver: Contact = None
        self.contact_mapped_by_message_id = defaultdict(Contact)
        self.messages_mapped_by_contact_id = defaultdict(list)
        self.contact_map = contact_map

        self.cloud = cloud
        self.target_key = target_key
        self.updater = config.create_updater()
        self.init_updater()
        self.cloud.set_target(target_key, self)

    def init_updater(self):
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.on_receive))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))
        self.updater.dispatcher.add_handler(CommandHandler("show_contacts", self.show_contacts))

        self.updater.start_polling()
        self.show_contacts(None, None)
        self.updater.bot.send_message(chat_id=TELEGRAM_ID, text="Ready")

    def send_info(self, text: str):
        self.updater.bot.send_message(chat_id=TELEGRAM_ID, text=text)

    def change_receiver(self, receiver: Contact):
        self.current_receiver = receiver
        self.send_info("当前会话切换至「{0}」。".format(receiver.name))

    def send_inline_keyboard(self, text, keyboard):
        reply_markup = InlineKeyboardMarkup(keyboard)
        return self.updater.bot.send_message(chat_id=TELEGRAM_ID, text=text, reply_markup=reply_markup)

    def make_contact_list_keyboard(self):
        keyboard = []
        cur_row = []
        for contact in self.contact_map.values():
            cur_row.append(make_inline_keyboard(contact.name, contact.id))
            if len(cur_row) == 3:
                keyboard.append(cur_row.copy())
                cur_row.clear()

        if len(cur_row) > 0:
            keyboard.append(cur_row)
        return keyboard

    def show_contacts(self, bot, update):
        self.cloud.refresh_coolq()
        self.send_inline_keyboard("所有联系方式", self.make_contact_list_keyboard())

    def on_button_click(self, bot, update):
        callback_data = int(update.callback_query.data)
        self.change_receiver(self.contact_map[callback_data])

    def on_receive(self, bot, update):
        if update.message.chat_id != TELEGRAM_ID:
            self.send_info("有外人尝试发消息给 forward-bot。")
            return
        if self.current_receiver is None:
            self.send_info("没有会话，无法发送消息。")
            return

        if update.message.reply_to_message is not None:
            new_receiver: Contact = self.contact_mapped_by_message_id[update.message.reply_to_message.message_id]
            if new_receiver.id != self.current_receiver.id:
                self.change_receiver(new_receiver)

        msg = Message(MESSAGE_TARGET_COOLQ,
                      self.current_receiver,
                      Content("text", update.message.text),
                      Contact(0, "OY_TG", self.current_receiver.type))
        self.on_message(msg)

    def on_message(self, message: Message):
        logging.info("[-> leaving from telegram] %s", message.content.value)
        self.cloud.push_cloud(message)

    def edit_message(self, message_id, text):
        self.updater.bot.edit_message_text(chat_id=TELEGRAM_ID, message_id=message_id, text=text)

    def send_message(self, message: Message):
        value = mark_up_message(message)
        logging.info("[<- sending to telegram] id: %s value: %s", TELEGRAM_ID, value)
        sent_message = self.updater.bot.send_message(chat_id=TELEGRAM_ID, text=value)
        if self.current_receiver is None:
            self.change_receiver(message.sender)

        self.contact_mapped_by_message_id[sent_message.message_id] = message.sender
        self.messages_mapped_by_contact_id[message.sender.id].append((sent_message, message))

