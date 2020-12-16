class SmsPilotAPIError(Exception):
    pass


class ApiKeyBlocked(SmsPilotAPIError):
    pass


class ApiSystemError(SmsPilotAPIError):
    pass


class NoMoneyError(SmsPilotAPIError):
    pass


class SenderNotRegistered(SmsPilotAPIError):
    pass


class SMSValidationError(Exception):
    pass


errors_types = {
    106: ApiKeyBlocked,
    110: ApiSystemError,
    112: NoMoneyError,
    204: SenderNotRegistered
}


def error_handle(data: dict):
    error = data.get('error', {})
    error_code = int(error.get('code', 0))
    error_description = error.get('description')

    exc_class = errors_types.get(error_code, SmsPilotAPIError)

    return exc_class(f"{error_code}: {error_description}")