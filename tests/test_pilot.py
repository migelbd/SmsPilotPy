import unittest
from sms_pilot import SmsPilot, objects, exception
from sms_pilot.callback import Callback

API_KEY = 'XXXXXXXXXXXXYYYYYYYYYYYYZZZZZZZZXXXXXXXXXXXXYYYYYYYYYYYYZZZZZZZZ'
PHONE = 79201112223


class SmsPilotTestCase(unittest.TestCase):

    def setUp(self):
        self.client = SmsPilot(API_KEY, 'INFORM')

    def test_user_info(self):
        user_info = self.client.user_info()

        self.assertIsInstance(user_info, objects.UserInfo)
        self.assertEqual(user_info.name, 'Букин Геннадий')

    def test_send_message(self):
        result = self.client.send_message(
            to=PHONE,
            text='Привет от Букина'
        )

        self.assertIsInstance(result, objects.MessageResponse)
        self.assertEqual(result.server_id, 10000)

        self.assertEqual(result.status, objects.RECEIVED)
        self.assertEqual(result.get_status_verbose(), 'Новое')
        self.assertEqual(result.phone, PHONE)

    def test_send_messages(self):
        prepare_message = [
            {
                'to': 79991111111,
                'text': 'Hello 1'
            },
            {
                'to': 79992222222,
                'text': 'Hello 2'
            },
            {
                'to': 79993333333,
                'text': 'Hello 3'
            }
        ]

        for msg in prepare_message:
            self.client.add_message(**msg)

        result = self.client.send_messages()
        self.assertEqual(len(result.send), 3)

    def test_callback(self):
        callback = Callback('https://smspilot.ru/callback', method='POST')
        client = SmsPilot(API_KEY, callback=callback)

        self.assertEqual(client._callback, callback)

    def test_callback_bad(self):
        callback = Callback('https://smspilot.ru/callback', method='DELETE')
        self.assertRaises(exception.SMSValidationError, callback.to_dict)

    def test_send_hlr(self):
        result = self.client.send_hlr(PHONE)
        self.assertIsInstance(result, objects.HlrResponse)
        self.assertEqual(result.status, objects.HlrResponse.ACCEPTED)

    def test_send_ping(self):
        result = self.client.ping(PHONE)
        self.assertIsInstance(result, objects.PingResponse)
        self.assertEqual(result.status, objects.PingResponse.ACCEPTED)

    def test_check_hlr(self):
        result = self.client.check_ping_hlr(10000)

        self.assertIsInstance(result, objects.CheckResponse)
        self.assertEqual(result.status, objects.CheckResponse.ERROR)

