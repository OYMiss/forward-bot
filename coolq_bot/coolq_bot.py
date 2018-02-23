from cqhttp import CQHttp

from constants import CHAT_TYPE_FRIEND, CHAT_TYPE_GROUP, decode_id, makeup_id


def read_config():
    coolq_config = open("./coolq_bot.config").read().split()
    coolq_bot = CQHttp(api_root='http://127.0.0.1:5700/',
                       secret=coolq_config[0][len("CQHTTP_SECRET="):],
                       access_token=coolq_config[1][len("CQHTTP_ACCESS_TOKEN="):])
    return coolq_bot


class CoolQBot:
    info = {"id_name": dict(),
            "cur_id": None}

    def __init__(self, forward_bot):
        self.coolq_bot = read_config()
        self.refresh()
        self.forward_bot = forward_bot

    def send_to_qq(self, text):
        qq_id = self.info["cur_id"]
        chat_type, raw_qq_id = decode_id(qq_id[0]), int(qq_id[1:])
        if chat_type == CHAT_TYPE_GROUP:
            self.coolq_bot.send_group_msg(group_id=raw_qq_id, message=text)
        elif chat_type == CHAT_TYPE_FRIEND:
            self.coolq_bot.send_private_msg(user_id=raw_qq_id, message=text)

    def get_cur_info(self):
        qq_id = self.info["cur_id"]
        if qq_id is None:
            return "当前没有聊天"
        name = self.info["id_name"][qq_id]

        tail = "\n... 类型:" + ("群" if decode_id(qq_id) == CHAT_TYPE_GROUP else "好友")
        return name + tail

    def change_current(self, qq_id):
        self.info["cur_id"] = qq_id

    def refresh(self):
        self.info["id_name"].clear()
        self.__init_friends()
        self.__init_groups()

    def __init_friends(self):
        for group in self.coolq_bot._get_friend_list():
            for friend in group.get("friends"):
                self.info["id_name"][makeup_id(friend.get("user_id"), CHAT_TYPE_FRIEND)] = friend.get("remark")

    def __init_groups(self):
        for group in self.coolq_bot.get_group_list():
            self.info["id_name"][makeup_id(group.get("group_id"), CHAT_TYPE_GROUP)] = group.get("group_name")

    def run(self):
        self.coolq_bot.on_message("private")(self.__handle_private_message)
        self.coolq_bot.on_message("group")(self.__handle_group_message)
        self.coolq_bot.on_request('group', 'friend')(self.__handle_request)
        self.coolq_bot.run(host='localhost', port=8889)

    def __no_current_when_msg_comes(self, qq_id):
        if self.info.get("cur_id") is None:
            self.info["cur_id"] = qq_id

    def __handle_private_message(self, context):
        qq_id = makeup_id(context.get("user_id"), CHAT_TYPE_FRIEND)
        name = self.info["id_name"][qq_id]
        self.__no_current_when_msg_comes(qq_id)

        text = name + ": " + context['message']
        self.forward_bot.send_to_telegram(text, qq_id)

    def __get_group_member_name(self, context):
        member = self.coolq_bot.get_group_member_info(group_id=context.get("group_id"), user_id=context.get('user_id'))
        name = member.get('card')
        if name == "":
            name = member['nickname']
        return name

    def __handle_group_message(self, context):
        qq_id = makeup_id(context.get("group_id"), CHAT_TYPE_GROUP)
        member_name = self.__get_group_member_name(context)
        self.__no_current_when_msg_comes(qq_id)

        text = member_name + ": " + context['message']
        suffix = "\n... from " + self.info["id_name"][qq_id]
        self.forward_bot.send_to_telegram(text, qq_id, tail=suffix)

    def __handle_request(self, context):
        self.forward_bot.send_to_telegram("有新的好友或群组")

