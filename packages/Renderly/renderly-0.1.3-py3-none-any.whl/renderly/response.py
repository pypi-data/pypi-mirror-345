class Response:

    STATUS_CODE = {
        200: "200 OK",
        201: "201 Created",
        204: "204 No Content",
        301: "301 Moved Permanently",
        302: "302 Found",
        400: "400 Bad Request",
        403: "403 Forbidden",
        404: "404 Not Found",
        500: "500 Internal Server Error",
        502: "502 Bad Gateway",
        503: "503 Service Unavailable",
    }

    def __init__(self, status=200, content_type="text/html"):
        self.status = Response.STATUS_CODE.get(status, 500)
        self._headers = [("Content-Type", content_type)]
        self._cookies = []

    def set_header(self, name, value):
        self._headers = [(k, v) for (k, v) in self._headers if k.lower() != name.lower()]
        self._headers.append((name, value))

    def set_cookie(self, key, value, path="/", httponly=False, secure=False,
                   expires=None, max_age=None, samesite=None):
        parts = [f"{key}={value}", f"Path={path}"]

        if max_age is not None:
            parts.append(f"Max-Age={int(max_age)}")

        if expires is not None:
            if isinstance(expires, (int, float)):
                expires = datetime.utcfromtimestamp(expires)
            if isinstance(expires, datetime):
                parts.append(f"Expires={format_datetime(expires, usegmt=True)}")

        if secure:
            parts.append("Secure")
        if httponly:
            parts.append("HttpOnly")
        if samesite:
            parts.append(f"SameSite={samesite}")

        cookie_header = "; ".join(parts)
        self._cookies.append(("Set-Cookie", cookie_header))

    def clear_cookies(self):
        self._cookies = []

    def redirect(self, url, status=302):
        self.status = Response.STATUS_CODE.get(status, 500)
        self.set_header("Location", url)

    def __call__(self):
        return self.status, self._headers + self._cookies

