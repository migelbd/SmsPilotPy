from sms_pilot.exception import SMSValidationError


def is_valid_url(url):
    import re
    regex = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


class Callback:

    def __init__(self, url, method: str = 'get'):
        self.url = url
        self.method = method

    def __validate(self):
        if not is_valid_url(self.url):
            raise SMSValidationError('Callback URL is invalid')
        if str(self.method).upper() not in ('GET', 'POST', 'PUT'):
            raise SMSValidationError('Callback method is invalid')

    def to_dict(self) -> dict:
        self.__validate()
        return dict(callback=self.url, callback_method=self.method)
