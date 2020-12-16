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


class Message:
    def __init__(self, **data):
        self.id = data.get('id')
        self.server_id = data.get('server_id')
        self.from_ = data.get('from')
        self.to = data.get('to')
        self.text = data.get('text')
        self.parts = data.get('parts')
        self.price = data.get('price')
        self.status = int(data.get('status'))
        self.error = data.get('error')
        self.send_datetime = data.get('send_datetime')
        self.country = data.get('country')
        self.operator = data.get('operator')

    def is_delivered(self) -> bool:
        return self.status == DELIVERED

    def is_error(self) -> bool:
        return self.status == ERROR

    def get_status_verbose(self) -> str:
        return get_status_dict().get(self.status)

    def __str__(self):
        return 'Message(%s): %s %s' % (self.id, self.to, self.get_status_verbose())

    def __repr__(self):
        return str(self)


class MessageResponse:

    def __init__(self, server_response: dict):
        self.send = [Message(**msg) for msg in server_response.get('send', [])]
        self.cost = server_response.get('cost')
        self.balance = server_response.get('balance')
        self.server_packet_id = server_response.get('server_packet_id')

    def __len__(self):
        return len(self.send)

    def __str__(self):
        return 'MessageResponse: %s' % self.server_packet_id

    def __repr__(self):
        return str(self)


class MessageCheck:

    def __init__(self, check: dict):
        self.id = check.get('id')
        self.server_id = check.get('id')
        self.status = check.get('status')
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
        self.id = info.get('id')
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
        return f'UserInfo: {self.name}'

    def __repr__(self):
        return str(self)
