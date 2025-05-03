from json import JSONDecodeError
from requests.models import Response
from deceit.exceptions import ApiException



class BigException(ApiException):
    def __init__(self, status_code=None, content=None, text=None, data=None):
        super().__init__(status_code, content, text, data)
        self.status_code = status_code
        self.content = content
        self.text = text
        self.data = data

    def __str__(self):
        klass = self.__class__.__name__.lower()
        return f'[{klass}] [{self.status_code}] {self.text}'

    @classmethod
    def from_response(cls, response: Response):
        try:
            return cls(
                response.status_code,
                response.content,
                response.text,
                response.json(),
            )
        except JSONDecodeError:
            return cls(
                response.status_code,
                response.content,
                response.text,
            )
