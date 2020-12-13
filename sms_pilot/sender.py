import json
from datetime import datetime
from typing import Optional, Union, List

import requests
from .callback import Callback
import sms_pilot.objects as objects
from .exception import error_handle


class PilotSender(object):
    api_url_v2 = "http://smspilot.ru/api2.php"
    api_url_v1 = "http://smspilot.ru/api.php"

    def __init__(self, api_key: str, default_sender: str = 'INFORM', callback: Callback = None, is_test: int = None, is_cost: int = None):
        self._callback = callback
        self._api_key = api_key
        self._default_sender = default_sender
        self.messages = []
        self._is_test = is_test
        self._is_cost = is_cost

    def _request_v2(self, data: dict) -> dict:
        data.update(dict(
            apikey=self._api_key
        ))
        if self._is_cost is not None:
            data['cost'] = self._is_cost
        if self._is_test is not None:
            data['test'] = self._is_test
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'SMSPilotPy/0.1'
        }
        response = requests.post(self.api_url_v2, json=data, headers=headers)
        response_data = response.json()
        if 'error' in response_data:
            raise error_handle(response_data)
        return response_data

    def __get_last_message_id(self) -> int:
        return len(self.messages) + 1

    def send_messages(self) -> objects.MessageResponse:
        data = {
            'send': self.messages
        }
        return objects.MessageResponse(self._request_v2(data))

    def add_message(self, to: Union[str, int], text: str, sender: str = None, **kwargs):
        callback_obj = kwargs.get('callback')
        time_to_live = kwargs.get('ttl')
        send_datetime = kwargs.get('send_datetime')
        msg = {
            'id': kwargs.get('id', self.__get_last_message_id()),
            'to': to,
            'from': sender or self._default_sender,
            'text': text
        }

        if isinstance(callback_obj, Callback):
            msg.update(callback_obj.to_dict())

        if isinstance(send_datetime, datetime):
            msg['send_datetime'] = send_datetime.strftime('%Y-%m-%d %H:%M:%S')

        if time_to_live:
            assert isinstance(time_to_live, int) and 1 <= time_to_live <= 1440, 'TTL может быть в диапозоне 1...1440'
            msg['ttl'] = time_to_live
        self.messages.append(msg)
        return self

    def check_by_server_id(self, server_ids: Union[int, List[int]]):
        if isinstance(server_ids, int):
            server_ids = [server_ids]
        data = {
            "check": {"server_id": v for v in server_ids}
        }
        return self._request_v2(data)

    def check_by_server_pocket_id(self, server_pocket_id: int):
        data = {
            'check': True,
            'server_pocket_id': server_pocket_id
        }

        return objects.MessageCheckResponse(self._request_v2(data))

    def get_balance(self, in_rur=True) -> Optional[float]:
        data = {
            'balance': 'rur' if in_rur else 'sms'
        }
        return self._request_v2(data).get('balance')

    def user_info(self) -> objects.UserInfo:
        return objects.UserInfo(self._request_v2(dict(info=True)))








# {'send': [{'id': 1, 'server_id': '164975610', 'from': 'INFORM', 'to': '79209291770', 'text': 'hello', 'parts': '1', 'status': '0', 'error': '0', 'send_datetime': '', 'country': 'RU', 'operator': 'MEGAFON', 'price': '2.55'}], 'server_packet_id': '164975610', 'balance': '646.66', 'cost': '2.55'}