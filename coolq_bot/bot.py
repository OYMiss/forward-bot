from cqhttp import CQHttp


class CooQBot:
    coolq_config = open("./coolq_bot.config").read().split()
    coolq_bot = CQHttp(api_root='http://127.0.0.1:5700/',
                       secret=coolq_config[0][len("CQHTTP_SECRET="):],
                       access_token=coolq_config[1][len("CQHTTP_ACCESS_TOKEN="):])

    cache = {"friends": None,
             "groups": None}

    current = {"id": None,
               "is group": None}

    def __init__(self, forward_bot):
        self.refresh()
        self.forward_bot = forward_bot

    def get_cache(self):
        return self.cache

    def send_to_qq(self, text):
        if self.current["is group"]:
            self.coolq_bot.send_group_msg(group_id=self.current["id"], message=text)
        else:
            self.coolq_bot.send_private_msg(user_id=self.current["id"], message=text)

    def get_cur_info(self):
        if self.current["id"] is None:
            return "当前没有聊天"
        tail = "\n... 类型:" + ("群" if self.current["is group"] else "好友")
        if self.current["is group"]:
            return self.cache["groups"][self.current["id"]] + tail
        else:
            return self.cache["friends"][self.current["id"]] + tail

    def change_current(self, qq_id, is_group):
        self.current["id"] = qq_id
        self.current["is group"] = is_group

    def refresh(self):
        self.__init_friends()
        self.__init_groups()

    def __init_friends(self):
        self.cache["friends"] = dict()
        for group in self.coolq_bot._get_friend_list():
            for friend in group.get("friends"):
                self.cache["friends"][friend.get("user_id")] = friend.get("remark")

    def __init_groups(self):
        self.cache["groups"] = dict()
        for group in self.coolq_bot.get_group_list():
            self.cache["groups"][group.get("group_id")] = group.get("group_name")

    def run(self):
        self.coolq_bot.on_message("private")(self.__handle_private_message)
        self.coolq_bot.on_message("group")(self.__handle_group_message)
        self.coolq_bot.on_event('group_increase')(self.__handle_group_increase)
        self.coolq_bot.on_event('group_increase')(self.__handle_group_increase)
        self.coolq_bot.on_request('group', 'friend')(self.__handle_request)
        self.coolq_bot.run(host='localhost', port=8889)

    def __handle_private_message(self, context):
        if self.current["id"] is None:
            self.current["id"] = context.get("user_id")
            self.current["is group"] = False
        self.forward_bot.send_to_telegram(self.cache["friends"][context.get("user_id")] + ": " + context['message'])

    def __handle_group_message(self, context):
        if self.current["id"] is None:
            self.current["id"] = context.get("group_id")
            self.current["is group"] = True

        member = self.coolq_bot.get_group_member_info(group_id=context.get("group_id"),
                                                      user_id=context.get('user_id'))
        name = member.get('card')
        if name == "":
            name = member['nickname']
        self.forward_bot.send_to_telegram(name + ": " + context['message']
                                          + "\n... from " + self.cache["groups"][context.get("group_id")])

    def __handle_group_increase(self, context):
        self.coolq_bot.send(context, message='欢迎新人～', is_raw=True)  # 发送欢迎新人

    def __handle_request(self, context):
        self.forward_bot.send_to_telegram("有新的好友或群组")
        # return {'approve': True}  # 同意所有加群、加好友请求

