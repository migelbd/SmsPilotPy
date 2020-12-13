class Message:
    def __init__(self, **data):
        self.id = data.get('id')
        self.server_id = data.get('server_id')
        self.from_ = data.get('from')
        self.to = data.get('to')
        self.text = data.get('text')
        self.parts = data.get('parts')
        self.price = data.get('price')
        self.status = data.get('status')
        self.error = data.get('error')
        self.send_datetime = data.get('send_datetime')
        self.country = data.get('country')
        self.operator = data.get('operator')


class MessageResponse:

    def __init__(self, server_response: dict):
        self.send = [Message(**msg) for msg in server_response.get('send', [])]
        self.cost = server_response.get('cost')
        self.balance = server_response.get('balance')
        self.server_packet_id = server_response.get('server_packet_id')


class MessageCheck:
    NOT_FOUND = -2
    NOT_DELIVERED = -1
    RECEIVED = 0
    OPERATOR = 1
    DELIVERED = 2
    POSTPONED = 3

    def __init__(self, check: dict):
        self.id = check.get('id')
        self.server_id = check.get('id')
        self.status = check.get('status')
        self.modified = check.get('modified')

    def is_delivered(self) -> bool:
        return self.status == self.DELIVERED


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

    def __repr__(self):
        return f'UserInfo: {self.name}'
