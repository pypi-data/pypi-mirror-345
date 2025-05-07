import json


class Response:
    def __init__(self, value, content_type: str, status_code: int = 200):
        self._value = value
        self.content_type = content_type
        self.status_code = status_code

    @property
    def value(self):
        return self._value


class JsonResponse(Response):
    def __init__(self, value, **kwargs):
        json_object = json.dumps(value)
        super().__init__(
            value=json_object.encode("utf-8"),
            content_type="application/json; charset=utf-8",
            **kwargs
        )


class ErrorResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, content_type="text/html", **kwargs)
