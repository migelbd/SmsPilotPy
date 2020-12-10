class Callback:

    def __init__(self, url, method: str = 'get'):
        self.url = url
        self.method = method

    def __validate(self):
        pass

    def to_dict(self) -> dict:
        self.__validate()
        return dict(callback=self.url, callback_method=self.method)
