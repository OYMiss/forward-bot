from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from coolq_bot import coolq_bot as qq_bot

# constants

HELLO_MESSAGE = "使用 /help 查看帮助。\n" \
                "使用 /change [群名称] 更改当前聊天。\n" \
                "使用 /current 查看当前聊天。\n" \
                "使用 /list_friends 查看所有好友\n" \
                "使用 /list_groups 查看所有群组"


# global variables
_bot = None
OYMISS_TOKEN = None
OY_TELEGRAM_ID = None
group_infos = None
group_keyboard = None
friend_infos = None
friend_keyboard = None

def dispatch_to_telegram(content):
    """
    used for qq_bot
    :param content: content to send
    :return: success?
    """
    print("sending")
    _bot.send_message(chat_id=OY_TELEGRAM_ID, text=content)
    print("dispatch to telegram", content)


def dispatch_inline_button(content, keyboard):
    reply_markup = InlineKeyboardMarkup(keyboard)
    _bot.send_message(chat_id=OY_TELEGRAM_ID, text=content, reply_markup=reply_markup)


def add_command_handler(cmd_name, cmd_fun, dispatcher):
    handler = CommandHandler(cmd_name, cmd_fun)
    dispatcher.add_handler(handler)
    print("add command", cmd_name)


def add_message_handler(dispatcher):
    dispatcher.add_handler(MessageHandler(Filters.text, on_receive))


def on_receive(bot, update):
    # check the user is OY?
    if update.message.chat_id != OY_TELEGRAM_ID:
        return

    qq_bot.dispatch_to_coolq(update.message.text)
    print("dispatch to qq", update.message.text)
    # dispatch to qq
    # qq_bot.dispatch_to_qq(cur_contact, update.message.text)


def button_fun(bot, update):
    print("button click")
    query = update.callback_query
    change_to(query.data)


def help_fun(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=HELLO_MESSAGE)
    print("help:", HELLO_MESSAGE)


def change_to(qq_id):
    is_group = False
    if qq_id[0] == '#':
        is_group = True
        qq_id = qq_id[1:]
    qq_id = int(qq_id)
    qq_bot.change_current(qq_id, is_group)
    now = group_infos[qq_id] if is_group else friend_infos[qq_id]
    _bot.send_message(chat_id=OY_TELEGRAM_ID, text="当前聊天发生了改变 -> " + now)


def change_fun(bot, update):
    qq_id = update.message.text[len("/change") + 1:len(update.message.text)]
    change_to(qq_id)


def current_fun(bot, update):
    if qq_bot.cur_id is None:
        current_chat = "当前没有聊天"
    else:
        current_chat = qq_bot.get_cur_info()

    bot.send_message(chat_id=OY_TELEGRAM_ID, text=current_chat)
    print("current", current_chat)


def init_inline_keyboard():
    global friend_infos, friend_keyboard

    friend_infos = dict()
    each_row = []
    friend_keyboard = []
    for key, value in qq_bot.mapping_friend_from_id_to_info.items():
        name = value.get('remark')
        if name == '':
            name = value.get('nickname')
        if len(each_row) % 2 == 0 and len(each_row) > 0:
            friend_keyboard.append(each_row.copy())
            each_row = []
        each_row.append(InlineKeyboardButton(name, callback_data=key))
        friend_infos[key] = name
    friend_keyboard.append(each_row)

    global group_infos, group_keyboard

    group_infos = dict()
    each_row = []
    group_keyboard = []
    for key, value in qq_bot.mapping_group_from_id_to_info.items():
        name = value.get('group_name')
        if len(each_row) % 2 == 0 and len(each_row) > 0:
            group_keyboard.append(each_row.copy())
            each_row = []
        each_row.append(InlineKeyboardButton(name, callback_data="#" + str(key)))
        group_infos[key] = name
    group_keyboard.append(each_row)


def refresh_fun(bot, update):
    qq_bot.init_groups()
    qq_bot.init_friends()
    init_inline_keyboard()
    dispatch_to_telegram("刷新列表完成")


def list_friends_fun(bot, update):
    dispatch_inline_button("所有好友：\n", friend_keyboard)


def list_groups_fun(bot, update):
    dispatch_inline_button("所有群组：\n", group_keyboard)


def init(BOT_TOKEN, YOUR_ID, is_proxy):
    global _bot, OYMISS_TOKEN, OY_TELEGRAM_ID
    OYMISS_TOKEN = BOT_TOKEN
    OY_TELEGRAM_ID = YOUR_ID

    from telegram.ext import Updater
    # init updater and proxy
    if is_proxy:
        updater = Updater(token=OYMISS_TOKEN, request_kwargs={
            'proxy_url': 'socks5://127.0.0.1:1080/'
        })
    else:
        updater = Updater(token=OYMISS_TOKEN)

    # init global _bot
    _bot = updater.bot

    # init handler
    add_command_handler("help", help_fun, updater.dispatcher)
    add_command_handler("change", change_fun, updater.dispatcher)
    add_command_handler("current", current_fun, updater.dispatcher)
    add_command_handler("refresh", refresh_fun, updater.dispatcher)
    add_command_handler("list_friends", list_friends_fun, updater.dispatcher)
    add_command_handler("list_groups", list_groups_fun, updater.dispatcher)
    add_message_handler(updater.dispatcher)

    updater.dispatcher.add_handler(CallbackQueryHandler(button_fun))

    # sort by Chinese
    # locale.setlocale('LC_COLLATE', 'zh_CN.UTF8')

    return updater


def run(BOT_TOKEN, YOUR_ID, is_proxy=False):
    init(BOT_TOKEN, YOUR_ID, is_proxy).start_polling()
