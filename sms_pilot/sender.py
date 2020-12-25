import json
from datetime import datetime
from typing import Optional, Union, List
import re
import requests
from .callback import Callback
import sms_pilot.objects as objects
from .exception import error_handle, SmsPilotAPIError, SMSValidationError


def validate_email(value: str) -> Optional[str]:
    if value is None:
        return value
    match = re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', value)
    if match:
        return match.group(0)
    return None


def validate_phone(value: Union[str, int]) -> Optional[int]:
    match = re.search(r'^7[0-9]{10}$', str(value))
    if not match:
        raise SMSValidationError('Phone invalid')
    return int(match.group(0))


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
        :keyword raw_response Если True возвращает dict на запросы
        """
        assert api_key, 'ApiKey not set'
        self._callback = callback
        self._api_key = api_key
        self._default_sender = default_sender
        self.debug = validate_email(options.get('debug'))
        self.messages = []
        self.is_test = options.get('test', False)
        self.is_cost = options.get('cost', False)
        self.raw_response = options.get('raw_response', False)
        self._format = options.get('format', 'json')
        if self._format != 'json':
            self.raw_response = True

    def prepare_request_data(self, data: dict) -> dict:
        data.update(dict(
            apikey=self._api_key,
            format=self._format if self._format in ('json', 'text', 'xml', 'v') else 'json'
        ))
        if self.is_cost is not None:
            data['cost'] = int(self.is_cost)
        if self.is_test is not None:
            data['test'] = int(self.is_test)
        if self.debug:
            data['debug'] = self.debug

        return data

    def _request(self, api_version: int, data: dict, method: str = 'POST') -> dict:
        from sms_pilot import __version__
        try:
            api_url = self.api_urls[api_version]
        except KeyError:
            raise SmsPilotAPIError('Не верная версия API')
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'SMSPilotPy/%s' % __version__
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

    def __extra_params(self, **data) -> dict:
        callback_obj = data.get('callback', self._callback)
        time_to_live = data.get('ttl')
        send_datetime = data.get('send_datetime')
        if isinstance(callback_obj, Callback):
            data.update(callback_obj.to_dict())

        if isinstance(send_datetime, datetime):
            data['send_datetime'] = send_datetime.strftime('%Y-%m-%d %H:%M:%S')

        if time_to_live:
            assert isinstance(time_to_live, int) and 1 <= time_to_live <= 1440, 'TTL может быть в диапозоне 1...1440'
            data['ttl'] = time_to_live
        return data

    def __get_last_message_id(self) -> int:
        return len(self.messages) + 1

    def send_message(self, to: Union[int, str], text: str, sender: str = None, **kwargs) -> Union[
        objects.MessageResponse, dict, str]:
        """
        Отправить одно сообщение

        :param to: Номер телефона
        :param text: Текст сообщения
        :param sender: Отправитель
        :param kwargs:
        :keyword callback Callback:
        :keyword ttl:
        :keyword send_datetime: Время отправки сообщения
        :return:
        """
        msg = {
            'to': validate_phone(to),
            'send': text,
            'from': sender or self._default_sender
        }
        msg.update(self.__extra_params(**kwargs))

        response = self._request(1, self.prepare_request_data(msg), 'GET')
        if self.raw_response:
            return response
        return objects.MessageResponse(response)

    def send_messages(self) -> Union[objects.MessagesResponse, dict, str]:
        """
        Отправить подготовленные сообщения

        :return:
        """
        data = {
            'send': self.messages
        }
        self.clear_messages()
        response = self._request(2, data)
        if self.raw_response:
            return response
        return objects.MessagesResponse(response)

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
        msg = {
            'id': kwargs.get('id', self.__get_last_message_id()),
            'to': validate_phone(to),
            'from': sender or self._default_sender,
            'text': text
        }
        msg.update(self.__extra_params(**kwargs))
        self.messages.append(msg)
        return self

    def clear_messages(self):
        """
        Очистка подготовленных сообщений

        :return:
        """
        self.messages = []

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

    def user_info(self) -> Union[objects.UserInfo, dict, str]:
        """
        Информация о пользователе

        :return:
        """
        response = self._request(2, dict(info=True))
        if self.raw_response:
            return response
        return objects.UserInfo(response)

    def send_hlr(self, to: Union[str, int], callback: Callback = None) -> Union[objects.HlrResponse, dict, str]:
        """
        HLR запрос

        :param to:
        :param callback:
        :return:
        """
        data = dict(send='HLR', to=to)
        if callback and isinstance(callback, Callback):
            data.update(callback.to_dict())
        response = self._request(1, data, 'GET')
        if self.raw_response:
            return response
        return objects.HlrResponse(response)

    def check_ping_hlr(self, server_id: Union[int, List[Union[int, str]]]) -> Union[objects.CheckResponse, dict, str]:
        """
        Проверка статусов запросов HLR или Ping

        :param server_id:
        :return:
        """
        if isinstance(server_id, list):
            server_id = ','.join(server_id)
        data = {
            'check': server_id
        }

        response = self._request(1, self.prepare_request_data(data), 'GET')
        if self.raw_response:
            return response
        return objects.CheckResponse(response)

    def ping(self, to: Union[str, int], callback: Callback = None) -> Union[objects.PingResponse, dict, str]:
        """
        PING запрос

        :param to:
        :param callback:
        :return:
        """
        data = dict(send='PING', to=to)
        if callback and isinstance(callback, Callback):
            data.update(callback.to_dict())
        response = self._request(1, data, 'GET')
        if self.raw_response:
            return response
        return objects.PingResponse(response)
