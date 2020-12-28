import requests
from time import sleep

URL = 'https://api.telegram.org/bot1377300202:AAHrZY0KokLcacdo_SriqiFLP6BIU5EyLFk/'


# returns response of telegram's api
def get_updates_by_json(request):
    params = {'timeout': 100, 'offset': None}
    response = requests.get(request + 'getUpdates', data=params).json()
    return response


# returns data of last message in chat
def last_update(data_get_updates_by_json):
    results = data_get_updates_by_json['result']
    total_updates = len(results) - 1
    return results[total_updates]


# returns chat_id of message in chat
def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id


# returns text of last message in chat
def get_last_message(update):
    last_message = update['message']['text']
    return last_message


# send message to chat
def send_message(chat, text):
    params = {'chat_id': chat, 'text': text}
    response = requests.get(URL + 'sendMessage', data=params)
    return response


def main():
    update_id = last_update(get_updates_by_json(URL))['update_id']
    while True:
        if update_id == last_update(get_updates_by_json(URL))['update_id']:
            send_message(get_chat_id(last_update(get_updates_by_json(URL))), get_last_message(last_update(get_updates_by_json(URL))))
            update_id += 1
        sleep(1)


if __name__ == '__main__':
    main()
