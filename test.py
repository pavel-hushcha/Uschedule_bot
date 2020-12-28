import requests

URL = 'https://api.telegram.org/bot1377300202:AAHrZY0KokLcacdo_SriqiFLP6BIU5EyLFk/'


def get_update():
    url = URL + 'getupdates'
    r = requests.get(url).json()
    chat_id = r['result'][-1]['message']['chat']['id']
    message_text = r['result'][-1]['message']['text']
    update_id = r['result'][-1]['update_id']
    return chat_id, message_text, update_id


def send_message(chat_id, text='I do not understand you'):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    requests.get(url)


chat_id, text, update_id = get_update()
send_message(chat_id, text)