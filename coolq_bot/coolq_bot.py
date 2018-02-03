# -*- coding: utf-8 -*-

from cqhttp import CQHttp
import telegram_bot.telegram_bot as tg_bot

# global variable
_bot = CQHttp(api_root='http://127.0.0.1:5700/', secret="", access_token="")
mapping_friend_from_id_to_info = {}
mapping_group_from_id_to_info = {}

cur_id = None
cur_type_is_group = False


def dispatch_to_coolq(content):
    if cur_type_is_group:
        _bot.send_group_msg(group_id=cur_id, message=content)
        print("send to group", cur_id)
    else:
        _bot.send_private_msg(user_id=cur_id, message=content)
        print("send to friend", cur_id)


def change_current(id, is_group=False):
    global cur_id, cur_type_is_group
    cur_id = id
    cur_type_is_group = is_group


@_bot.on_message("private")
def handle_private_message(context):
    global cur_id, cur_type_is_group
    if cur_id is None:
        cur_id = context.get("user_id")
        cur_type_is_group = False

    tg_bot.dispatch_to_telegram(mapping_friend_from_id_to_info[context.get("user_id")]['remark'] + ": " + context['message'])
    # return {'reply': context['message'], 'at_sender': False}


@_bot.on_message("group")
def handle_private_message(context):
    global cur_id, cur_type_is_group
    if cur_id is None:
        cur_id = context.get("group_id")
        cur_type_is_group = True
    group = mapping_group_from_id_to_info[context.get("group_id")]
    member = _bot.get_group_member_info(group_id=group.get('group_id'), user_id=context.get('user_id'))

    name = member.get('card')
    if name == "":
        name = member['nickname']
    tg_bot.dispatch_to_telegram(name + ": " + context['message'] + "\n... from [G]" + group.get('group_name'))
    # return {'reply': context['message'], 'at_sender': False}


@_bot.on_event('group_increase')
def handle_group_increase(context):
    _bot.send(context, message='欢迎新人～', is_raw=True)  # 发送欢迎新人


@_bot.on_request('group', 'friend')
def handle_request(context):
    return {'approve': True}  # 同意所有加群、加好友请求


def init_friends(force=False):
    print("init friends")
    global mapping_friend_from_id_to_info
    if len(mapping_friend_from_id_to_info) > 0 and not force:
        return
    all_group = _bot._get_friend_list()
    for group in all_group:
        friends = group.get("friends")

        for friend in friends:
            qq_id = friend.get("user_id")
            mapping_friend_from_id_to_info[qq_id] = friend


def init_groups(force=False):
    print("init groups")
    global mapping_group_from_id_to_info
    if len(mapping_group_from_id_to_info) > 0 and not force:
        return
    all_groups = _bot.get_group_list()
    for group in all_groups:
        mapping_group_from_id_to_info[group.get("group_id")] = group


def run():
    init_friends()
    init_groups()
    _bot.run(host='localhost', port=8889)

