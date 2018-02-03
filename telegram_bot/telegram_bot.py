from telegram.ext import MessageHandler, Filters, CommandHandler
from coolq_bot import coolq_bot as qq_bot

# constants
OYMISS_TOKEN = '531873226:AAENKkuWHYLhl982OS6HwRgZwZvokQzoBew'
OY_TELEGRAM_ID = 404348187

HELLO_MESSAGE = "使用 /help 查看帮助。\n" \
                "使用 /change [群名称] 更改当前聊天。\n" \
                "使用 /current 查看当前聊天。\n" \
                "使用 /list_friends 查看所有好友\n" \
                "使用 /list_groups 查看所有群组"


# global variables
_bot = None


def dispatch_to_telegram(content, telegram_id=OY_TELEGRAM_ID):
    """
    used for qq_bot
    :param telegram_id: the telegram id binding with the qq_bot
    :param content: content to send
    :return: success?
    """

    _bot.send_message(chat_id=telegram_id, text=content)
    print("dispatch_to_telegram", content)


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


def help_fun(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=HELLO_MESSAGE)
    print("help", HELLO_MESSAGE)


def change_fun(bot, update):
    qq_id = update.message.text[len("/change") + 1:len(update.message.text)]
    is_group = False
    if qq_id[0] == '#':
        is_group = True
        qq_id = qq_id[1:]

    qq_bot.change_current(qq_id, is_group)
    bot.send_message(chat_id=OY_TELEGRAM_ID, text="当前聊天发生了改变 -> " + qq_id)


def current_fun(bot, update):
    if qq_bot.cur_id is None:
        current_chat = "当前没有聊天"
    else:
        current_chat = qq_bot.cur_id + "\n... 类型:" + ("群" if qq_bot.cur_type_is_group else "朋友")
    bot.send_message(chat_id=OY_TELEGRAM_ID, text=current_chat)
    print("current", current_chat)


def list_friends_fun(bot, update):
    qq_bot.init_groups(True)

    print("listing")
    all_friends = qq_bot.mapping_friend_from_id_to_info
    infos = []
    for key, value in all_friends.items():
        name = value.get('remark')
        if name == '':
            name = value.get('nickname')
        infos.append((name, key))

    friend_list = "\n 所有好友：\n"
    for name, qq_id in infos:
        friend_list += name + ": " + str(qq_id) + '\n'
    dispatch_to_telegram(friend_list)


def list_groups_fun(bot, update):
    print("listing")
    qq_bot.init_groups(True)
    all_groups = qq_bot.mapping_group_from_id_to_info

    infos = []
    for key, value in all_groups.items():
        name = value.get('group_name')
        infos.append((name, key))
    group_list = "\n 所有群组：\n"
    for name, qq_id in infos:
        group_list += name + "：" + str(qq_id) + "\n"
    dispatch_to_telegram(group_list)


def init():
    from telegram.ext import Updater
    # init updater and proxy
    updater = Updater(token=OYMISS_TOKEN, request_kwargs={
        'proxy_url': 'socks5://127.0.0.1:1080/'
    })

    # init global _bot
    global _bot
    _bot = updater.bot

    # init handler
    add_command_handler("help", help_fun, updater.dispatcher)
    add_command_handler("change", change_fun, updater.dispatcher)
    add_command_handler("current", current_fun, updater.dispatcher)
    add_command_handler("list_friends", list_friends_fun, updater.dispatcher)
    add_command_handler("list_groups", list_groups_fun, updater.dispatcher)
    add_message_handler(updater.dispatcher)

    # sort by Chinese
    # locale.setlocale('LC_COLLATE', 'zh_CN.UTF8')

    return updater


def run():
    init().start_polling()
