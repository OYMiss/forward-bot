CHAT_TYPE_FRIEND = 0
CHAT_TYPE_GROUP = 1
CHAT_TYPE_GROUP_PREFIX = '#'
CHAT_TYPE_FRIEND_PREFIX = '@'
TYPE_SUFFIX = {CHAT_TYPE_FRIEND: CHAT_TYPE_FRIEND_PREFIX,
               CHAT_TYPE_GROUP: CHAT_TYPE_GROUP_PREFIX}


def decode_id(qq_id):
    assert qq_id[0] == CHAT_TYPE_GROUP_PREFIX or qq_id[0] == CHAT_TYPE_FRIEND_PREFIX
    if qq_id[0] == CHAT_TYPE_GROUP_PREFIX:
        return CHAT_TYPE_GROUP
    elif qq_id[0] == CHAT_TYPE_FRIEND_PREFIX:
        return CHAT_TYPE_FRIEND


def makeup_id(qq_id, chat_type):
    return TYPE_SUFFIX[chat_type] + str(qq_id)