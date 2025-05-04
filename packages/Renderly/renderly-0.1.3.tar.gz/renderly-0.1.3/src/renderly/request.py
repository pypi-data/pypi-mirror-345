from urllib.parse import parse_qs
from http.cookies import SimpleCookie
import json


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.path = environ.get("PATH_INFO", "/")
        self.query_string = environ.get("QUERY_STRING", "")
        self.query = parse_qs(self.query_string)

        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.headers = self._parse_headers()
        self.cookies = self._parse_cookies()

        self._body = None
        self._form = None
        self._json = None

    def _parse_headers(self):
        headers = {}
        for key, value in self.environ.items():
            if key.startswith("HTTP_"):
                header = key[5:].replace("_", "-").title()
                headers[header] = value
        if 'CONTENT_TYPE' in self.environ:
            headers['Content-Type'] = self.environ['CONTENT_TYPE']
        if 'CONTENT_LENGTH' in self.environ:
            headers['Content-Length'] = self.environ['CONTENT_LENGTH']
        return headers

    def _parse_cookies(self):
        raw = self.environ.get("HTTP_COOKIE", "")
        cookies = SimpleCookie()
        cookies.load(raw)
        return {k: v.value for k, v in cookies.items()}

    @property
    def body(self):
        if self._body is None:
            try:
                content_length = int(self.environ.get("CONTENT_LENGTH", 0))
            except (ValueError, TypeError):
                content_length = 0

            self._body = self.environ["wsgi.input"].read(content_length) if content_length > 0 else b""
        return self._body

    @property
    def form(self):
        if self._form is None:
            if self.method == "POST" and "application/x-www-form-urlencoded" in self.headers.get("Content-Type", ""):
                body_str = self.body.decode("utf-8")
                self._form = parse_qs(body_str)
            else:
                self._form = {}
        return self._form

    @property
    def json(self):
        if self._json is None:
            if "application/json" in self.headers.get("Content-Type", ""):
                try:
                    self._json = json.loads(self.body.decode("utf-8"))
                except json.JSONDecodeError:
                    self._json = None
            else:
                self._json = None
        return self._json
