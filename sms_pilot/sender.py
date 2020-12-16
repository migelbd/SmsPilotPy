import json
from datetime import datetime
from typing import Optional, Union, List

import requests
from .callback import Callback
import sms_pilot.objects as objects
from .exception import error_handle, SmsPilotAPIError


class SmsPilot:
    api_urls = {
        1: 'http://smspilot.ru/api.php',
        2: 'http://smspilot.ru/api2.php'
    }

    def __init__(self, api_key: str, default_sender: str = 'INFORM', callback: Callback = None, **options):
        """
        SmsPilot

        :param api_key: Ключ API
        :param default_sender: Отправитель по умолчанию
        :param callback: Колл-бэк
        :param options:
        :keyword test: Тестовый режим (без передачи оператору)
        :keyword cost: Получить только стоимость
        """
        self._callback = callback
        self._api_key = api_key
        self._default_sender = default_sender
        self.messages = []
        self._is_test = options.get('test', False)
        self._is_cost = options.get('cost', False)

    def prepare_request_data(self, data: dict):
        data.update(dict(
            apikey=self._api_key,
            format='json'
        ))
        if self._is_cost is not None:
            data['cost'] = int(self._is_cost)
        if self._is_test is not None:
            data['test'] = int(self._is_test)
        return data

    def _request(self, api_version: int, data: dict, method: str = 'POST') -> dict:
        try:
            api_url = self.api_urls[api_version]
        except KeyError:
            raise SmsPilotAPIError('Не верная версия API')
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'SMSPilotPy/0.1'
        }
        if method == 'POST':
            response = requests.post(api_url, json=self.prepare_request_data(data), headers=headers)
        elif method == 'GET':
            response = requests.get(api_url, params=self.prepare_request_data(data), headers=headers)
        else:
            raise SmsPilotAPIError('Allowed GET or POST')
        if response.status_code != 200:
            raise SmsPilotAPIError('SomeError')

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            raise SmsPilotAPIError(response.text)
        if 'error' in response_data:
            raise error_handle(response_data)

        return response_data

    def __get_last_message_id(self) -> int:
        return len(self.messages) + 1

    def send_message(self, to: Union[int, str], text: str, sender: str = None, **kwargs):
        """
        Отправить отдно сообщение

        :param to: Номер телефона
        :param text: Текст сообщения
        :param sender: Отправитель
        :param kwargs:
        :keyword callback Callback:
        :keyword ttl:
        :keyword send_datetime: Время отправки сообщения
        :return:
        """
        self.add_message(to, text, sender, **kwargs)
        return self.send_messages()

    def send_messages(self) -> objects.MessageResponse:
        """
        Отправить подготовленные сообщения

        :return:
        """
        data = {
            'send': self.messages
        }
        self.messages = []
        return objects.MessageResponse(self._request(2, data))

    def add_message(self, to: Union[str, int], text: str, sender: str = None, **kwargs):
        """
        Добавить сообщение в список

        :param to: Номер телефона
        :param text: Текст сообщения
        :param sender: Отправитель
        :param kwargs:
        :keyword callback Callback:
        :keyword ttl:
        :keyword send_datetime: Время отправки сообщения
        :return:
        """
        callback_obj = kwargs.get('callback', self._callback)
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
        return self._request(2, data)

    def check_by_server_pocket_id(self, server_pocket_id: int):
        data = {
            'check': True,
            'server_pocket_id': server_pocket_id
        }

        return objects.MessageCheckResponse(self._request(2, data))

    def get_balance(self, in_rur=True) -> Optional[float]:
        """
        Баланс

        :param in_rur: В рублях
        :return:
        """
        data = {
            'balance': 'rur' if in_rur else 'sms'
        }
        return self._request(2, data).get('balance')

    def user_info(self) -> objects.UserInfo:
        """
        Информация о пользователе

        :return:
        """
        return objects.UserInfo(self._request(2, dict(info=True)))

    def send_hlr(self, to: Union[str, int], callback: Callback = None) -> objects.MessageResponse:
        """
        HLR запрос

        :param to:
        :param callback:
        :return:
        """
        data = dict(send='HLR', to=to)
        if callback and isinstance(callback, Callback):
            data.update(callback.to_dict())
        return objects.MessageResponse(self._request(1, data, 'GET'))

    def ping(self, to: Union[str, int], callback: Callback = None) -> objects.MessageResponse:
        """
        PING запрос

        :param to:
        :param callback:
        :return:
        """
        data = dict(send='PING', to=to)
        if callback and isinstance(callback, Callback):
            data.update(callback.to_dict())
        return objects.MessageResponse(self._request(1, data, 'GET'))
