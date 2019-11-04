import threading
import copy
import time

from constant import POST_PORT, POST_HOST
from main import *
from cqhttp import CQHttp


class CoolQBotConfig:
    def __init__(self, api_root, secret, access_token):
        self.api_root = api_root
        self.secret = secret
        self.access_token = access_token

    def create_coolq_bot(self):
        coolq_bot = CQHttp(api_root=self.api_root,
                           secret=self.secret,
                           access_token=self.access_token)
        return coolq_bot


class CoolQThread (threading.Thread):
    def __init__(self, coolq_bot):
        threading.Thread.__init__(self)
        self.coolq_bot = coolq_bot

    def run(self):
        self.coolq_bot.run(host=POST_HOST, port=POST_PORT)


class CoolQBot:
    def __init__(self, cloud: Cloud, target_key: int, config: CoolQBotConfig):
        self.friend_map = dict()
        self.group_map = dict()
        self.cloud = cloud
        self.target_key = target_key
        self.coolq_bot = config.create_coolq_bot()
        self.init_coolq_bot()
        self.cloud.set_target(self.target_key, self)

    def get_contact_map(self):
        return self.friend_map, self.group_map

    def init_friends(self):
        for friend in self.coolq_bot.get_friend_list():
            id = friend.get("user_id")
            name = friend.get("remark")
            assert(type(id) == int)
            contact = Contact(id, name)
            self.friend_map[id] = contact

    def init_groups(self):
        for group in self.coolq_bot.get_group_list():
            id = group.get("group_id")
            name = group.get("group_name")
            contact = Contact(id, name, CONTACT_TYPE_GROUP)
            self.group_map[id] = contact

    def init_coolq_bot(self):
        self.coolq_bot.on_message("private")(self.handle_private_message)
        self.coolq_bot.on_message("group")(self.handle_group_message)
        CoolQThread(self.coolq_bot).start()
        while True:
            try:
                status = self.coolq_bot.get_status()
            except Exception as e:
                time.sleep(1)
                logging.info("thread is waiting until QQ is online")
            else:
                if status['online']:
                    break

        self.init_friends()
        self.init_groups()

    def get_group_member_name(self, context):
        member = self.coolq_bot.get_group_member_info(group_id=context.get("group_id"), user_id=context.get('user_id'))
        name = member.get('card')
        if name == "":
            name = member['nickname']
        return name

    def parse_content(self, data):
        print(data)
        if data['type'] == 'text':
            # just append
            return Content(data['type'], data['data']['text'])
        elif data['type'] == 'share':
            # just append
            return Content(data['type'], data['data']['url'])
        elif data['type'] == 'rich':
            # just append
            return Content(data['type'], data['data']['content'])
        elif data['type'] == 'emoji':
            # just append
            return Content(data['type'], data['data']['id'])
        elif data['type'] == 'at':
            # just append
            return Content(data['type'], '@' + data['data']['qq'])
        elif data['type'] == 'rps':
            # just append
            return Content(data['type'], '【石头剪刀布】' + data['data']['type'])
        elif data['type'] == 'shake':
            # just append
            return Content(data['type'], '【戳一戳】')
        elif data['type'] == 'dice':
            # just append
            return Content(data['type'], '【骰子】' + data['data']['type'])
        elif data['type'] == 'location':
            # just append
            return Content(data['type'], '【位置】' + data['data']['title'] + ":" + data['data']['content'])
        elif data['type'] == 'sign':
            # just append
            return Content(data['type'], '【群签到】' + data['data']['location'])
        elif data['type'] == 'music':
            # just append
            if data['type'] == 'custom':
                return Content(data['type'], '【音乐】' + data['data']['type'] + str(data['data']['id']))
            else:
                return Content(data['type'], data['data']['url'])
        elif data['type'] == 'image':
            if 'url' in data['data']:
                return Content(data['type'], data['data']['url'])
            else:
                return Content('text', data['data']['file'])
            # if data['data'][file].endswith('.gif'):
            #     return Content('gif', data['data'][url])
            # else:
            #     return Content(data['type'], data['data'][url])
        elif data['type'] == 'face':
            return Content(data['type'], data['data']['id'])
        elif data['type'] == 'bface':
            return Content(data['type'], data['data']['id'])
        elif data['type'] == 'sface':
            return Content(data['type'], data['data']['id'])
        elif data['type'] == 'record':
            return Content(data['type'], data['data']['file'])

    def package_to_content(self, message):
        contents = []
        for content in message:
            print(content)
            contents.append(self.parse_content(content))
        return contents

    def handle_private_message(self, context):
        qq_id = context.get("user_id")
        # text = context['message']
        contents = self.package_to_content(context['message'])
        assert(type(qq_id) == int)
        assert(self.friend_map.get(qq_id, None) is not None)

        msg = Message(MESSAGE_TARGET_TELEGRAM_FRIEND,
                      Contact(0, "OY_TG"),
                      contents,
                      self.friend_map[qq_id])
        self.on_message(msg)

    def handle_group_message(self, context):
        qq_id = context.get("group_id")
        # text = context['message']
        contents = self.package_to_content(context['message'])
        assert(type(qq_id) == int)
        assert(self.group_map.get(qq_id, None) is not None)

        group_sender: Contact = copy.copy(self.group_map[qq_id])
        group_sender.sender_name = self.get_group_member_name(context)

        msg = Message(MESSAGE_TARGET_TELEGRAM_GROUP,
                      Contact(0, "OY_TG", CONTACT_TYPE_GROUP),
                      contents,
                      group_sender)
        self.on_message(msg)

    def on_message(self, message: Message):
        # logging.info("[<- leaving from coolq] %s", message.content.value)
        self.cloud.push_cloud(message)

    def send_message(self, message: Message):
        qq_id = message.receiver.id
        for content in message.contents:
            value = content.value
            # logging.info("[-> sending to coolq] id: %s value: %s", qq_id, value)
            if message.receiver.type == CONTACT_TYPE_GROUP:
                self.coolq_bot.send_group_msg(group_id=qq_id, message=value)
            else:
                self.coolq_bot.send_private_msg(user_id=qq_id, message=value)
