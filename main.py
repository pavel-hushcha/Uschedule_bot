import requests


# class Bot
class Bot:

    # class constructor
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    # returns chat updates
    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    # send message to chat
    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.get(self.api_url + method, params)
        return resp

    # returns last update of chat
    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]

        return last_update


echo_bot = Bot('1377300202:AAHrZY0KokLcacdo_SriqiFLP6BIU5EyLFk')


def main():
    new_offset = None

    while True:
        echo_bot.get_updates(new_offset)

        last_update = echo_bot.get_last_update()

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']

        echo_bot.send_message(last_chat_id, last_chat_text)

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
