import unittest
import src.Ushedule_bot.main as test_app
import requests


class UsheduleBotTests(unittest.TestCase):

    def setUp(self):
        self.bot = test_app.echo_bot

    def test_get_updates(self):
        t = self.bot.get_updates()
        self.assertIsInstance(t, list)

    def test_last_update(self):
        t = self.bot.get_updates()
        if len(t) == 0:
            self.assertEqual(t, [])
        else:
            self.assertIsInstance(t, list)

    def test_send_message(self):
        chat_id = self.bot.get_last_update()['message']['chat']['id']
        params = {'chat_id': chat_id, 'text': 'test'}
        requests.post('https://api.telegram.org/bot1377300202:AAHrZY0KokLcacdo_SriqiFLP6BIU5EyLFk/' + 'sendMessage', params)
        self.assertEqual(self.bot.get_last_update()['message']['text'], 'test')


if __name__ == '__main__':
    unittest.main()