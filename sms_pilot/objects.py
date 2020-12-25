from abc import ABC
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

ERROR = -2
NOT_DELIVERED = -1
RECEIVED = 0
OPERATOR = 1
DELIVERED = 2
POSTPONED = 3

MESSAGE_STATUSES = (
    (ERROR, 'Ошибка', 'Ошибка, неправильные параметры запроса'),
    (NOT_DELIVERED, 'Не доставлено',
     'Сообщение не доставлено (не в сети, заблокирован, не взял трубку), PING - не в сети, HLR - не обслуживается (заблокирован)'),
    (RECEIVED, 'Новое', 'Новое сообщение/запрос, ожидает обработки у нас на сервере'),
    (OPERATOR, 'В очереди', 'Сообщение или запрос ожидают отправки на сервере оператора'),
    (DELIVERED, 'Доставлено', 'Доставлено, звонок совершен, PING - в сети, HLR - обслуживается'),
    (POSTPONED, 'Отложено', 'Отложенная отправка, отправка сообщения/запроса запланирована на другое время'),
)


def get_status_dict(short=True) -> dict:
    if short:
        return dict([(code, short) for code, short, description in MESSAGE_STATUSES])
    return dict([(code, description) for code, short, description in MESSAGE_STATUSES])


class MessageBase(ABC):
    def is_delivered(self) -> bool:
        return self.status == DELIVERED

    def is_error(self) -> bool:
        return self.status == ERROR

    def get_status_verbose(self) -> str:
        return get_status_dict().get(self.status)


class MessageResponse(MessageBase):

    def __init__(self, server_response: dict):
        msg_obj = server_response.get('send', [])[-1]
        self.server_id = int(msg_obj.get('server_id', 0))
        self.phone = int(msg_obj.get('phone', 0))
        self.price = float(msg_obj.get('price', 0))
        self.status = int(msg_obj.get('status', 0))
        self.sender = msg_obj.get('sender')
        self.sender_orig = msg_obj.get('sender_orig')
        try:
            self.created = datetime.strptime(msg_obj.get('created'), DATE_FORMAT)
        except (ValueError, TypeError):
            self.created = None
        try:
            self.modified = datetime.strptime(msg_obj.get('modified'), DATE_FORMAT)
        except (ValueError, TypeError):
            self.modified = None
        self.parts = int(msg_obj.get('parts', 0))
        self.country = msg_obj.get('country')
        self.operator = msg_obj.get('operator')
        self.error = int(msg_obj.get('error', 0))
        self.error_en = msg_obj.get('error_en')
        self.error_ru = msg_obj.get('error_ru')
        self.message = msg_obj.get('message')
        self.balance = float(server_response.get('balance'))
        self.cost = float(server_response.get('cost', 0))

    def is_success(self):
        return self.error == 0

    def __str__(self):
        return 'MessageResponse: %s (%s)' % (self.phone, self.error_en)


class Message(MessageBase):
    def __init__(self, **data):
        self.id = int(data.get('id'))
        self.server_id = int(data.get('server_id'))
        self.from_ = data.get('from')
        self.to = int(data.get('to'))
        self.text = data.get('text')
        self.parts = int(data.get('parts'))
        self.price = float(data.get('price'))
        self.status = int(data.get('status'))
        self.error = data.get('error')

        try:
            self.send_datetime = datetime.strptime(data.get('send_datetime'), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            self.send_datetime = None

        self.country = data.get('country')
        self.operator = data.get('operator')

    def __str__(self):
        return 'Message(%s): %s %s' % (self.id, self.to, self.get_status_verbose())

    def __repr__(self):
        return str(self)


class MessagesResponse:

    def __init__(self, server_response: dict):
        self.send = [Message(**msg) for msg in server_response.get('send', [])]
        self.cost = float(server_response.get('cost', 0))
        self.balance = float(server_response.get('balance', 0))
        self.server_packet_id = int(server_response.get('server_packet_id', 0))

    def __len__(self):
        return len(self.send)

    def __str__(self):
        return 'MessageResponse: %s' % self.server_packet_id


class MessageCheck(MessageBase):

    def __init__(self, check: dict):
        self.id = int(check.get('id', 0))
        self.server_id = int(check.get('id', 0))
        self.status = int(check.get('status', ERROR))
        self.modified = check.get('modified')

    def is_delivered(self) -> bool:
        return self.status == DELIVERED


class MessageCheckResponse:
    def __init__(self, server_response: dict):
        self.raw_response = server_response
        self.check = [MessageCheck(check) for check in server_response.get('check', [])]


class UserInfo:
    def __init__(self, server_response):
        info = server_response.get('info', {})
        self.id = int(info.get('id'))
        self.tariff_id = info.get('tariff_id')
        self.email = info.get('email')
        self.phone = info.get('phone')
        self.name = info.get('name')
        self.balance = info.get('balance')
        self.date = info.get('date')
        self.senders = info.get('senders')
        self.default_sender = info.get('default_sender')
        self.any_sender = info.get('any_sender')

    def __str__(self):
        return 'UserInfo: %s' % self.name

    def __repr__(self):
        return str(self)


class PingResponseBase:
    ERROR = -2
    OUT_OF_SERVICE = -1
    ACCEPTED = 0
    SENT_TO_OPERATOR = 1
    PHONE_NUMBER_SERVED = 2
    STATUS_VERBOSE = (
        (ERROR, 'Запрос не принят, неправильный номер, ID не найден'),
        (OUT_OF_SERVICE, 'Номер не обслуживается'),
        (ACCEPTED, 'Запрос принят'),
        (SENT_TO_OPERATOR, 'Запрос передан оператору'),
        (PHONE_NUMBER_SERVED, 'Номер обслуживается'),
    )

    def __init__(self, server_response: dict):
        self.cost = float(server_response.get('cost', 0))
        self.balance = float(server_response.get('balance', 0))
        msg_obj = server_response.get('send', [{}])[-1]
        self.server_id = int(msg_obj.get('server_id', 0))
        self.phone = int(msg_obj.get('phone', 0))
        self.price = float(msg_obj.get('price', 0))
        self.status = int(msg_obj.get('status', 0))

    def is_served(self) -> bool:
        return self.status == self.PHONE_NUMBER_SERVED

    def is_ot_of_service(self) -> bool:
        return self.status == self.OUT_OF_SERVICE

    def get_verbose_status(self) -> str:
        status_dict = {code: description for code, description in self.STATUS_VERBOSE}
        return status_dict.get(self.status, '')


class HlrResponse(PingResponseBase):
    pass


class PingResponse(PingResponseBase):
    pass


class CheckResponse(PingResponseBase):
    def __init__(self, server_response: dict):
        super(CheckResponse, self).__init__(server_response)
        check = server_response.get('check', [{}])[-1]
        self.server_id = int(check.get('server_id', 0))
        phone = check.get('phone', 0)
        self.phone = int(phone) if phone != '' else None
        self.price = float(check.get('price', 0))
        self.status = int(check.get('status', 0))
