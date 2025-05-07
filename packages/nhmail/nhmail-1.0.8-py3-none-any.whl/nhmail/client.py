import json

from requests import Request, Session


class ServiceHttpClient:
    """
    use:
    ServiceHttpClient('https://nh-xxx.nandh.vn/').execute('get','v1/users/xxx')
    """

    JSON_CONTENT_TYPE = "application/json"

    def __init__(self, base_url, *args, **kwargs):
        self.base_url = base_url

    def get_full_url(self, uri):
        if "http" in uri:
            return uri

        return "/".join([self.base_url, uri])

    def get_http_headers(self):
        return {
            "system": "ops",
            "Content-Type": self.JSON_CONTENT_TYPE,
        }

    def get_default_params(self):
        return {}

    def get_content_type(self, content_type):
        return content_type.partition(";")[0].strip()

    def parse_request(self, uri, method, body, headers=None):
        method = method.upper()
        url = self.get_full_url(uri=uri)
        http_headers = self.get_http_headers()
        if headers:
            http_headers.update(headers)
        self._validate_headers(http_headers)
        req = Request(method, url, headers=http_headers)
        if body:
            if req.method in ["POST", "PUT", "PATCH"]:
                if (
                    not http_headers
                    or http_headers.get("Content-Type") == self.JSON_CONTENT_TYPE
                ):
                    req.json = body
                else:
                    req.data = body
            else:
                req.params = body

        return req

    def format_response(self, response):
        log = {
            "is_ok": response.ok,
            "status_code": response.status_code,
            "message": None,
            "raw_content": response.text,
            "json_content": None,
        }

        if response.status_code >= 500:
            content = "Please try again after a few minutes."
        else:
            try:
                content = response.json()
                log["json_content"] = content
            except json.JSONDecodeError as ex:
                log["message"] = str(ex)
                content = response.text
        return content

    def execute(self, method, uri, body=None, headers=None, timeout=10):
        try:
            parameter = self.get_default_params().copy()

            if body:
                if isinstance(body, list):
                    parameter = body
                else:
                    parameter.update(body)

            request = self.parse_request(uri, method, parameter, headers=headers)
            prepped = request.prepare()
            with Session() as session:
                response = session.send(prepped, timeout=timeout)

            response = self.format_response(response)

        except Exception as ex:
            print(ex)
            return None
        return response

    def _validate_headers(self, headers):
        if not headers:
            return
        for key, value in headers.items():
            try:
                str(value).encode("ascii")
            except UnicodeEncodeError:
                raise ValueError(
                    f"{key} header has invalid value '{value}'. "
                    f"Header values must be valid ASCII strings."
                )

    def get(self, uri, params=None, headers=None, timeout=30):
        return self.execute("get", uri, body=params, headers=headers, timeout=timeout)

    def post(self, uri, data=None, headers=None, timeout=30):
        return self.execute("post", uri, body=data, headers=headers, timeout=timeout)

    def patch(self, uri, data=None, headers=None, timeout=30):
        return self.execute("patch", uri, body=data, headers=headers, timeout=timeout)

    def put(self, uri, data=None, headers=None, timeout=30):
        return self.execute("put", uri, body=data, headers=headers, timeout=timeout)

    def delete(self, uri, params=None, headers=None, timeout=30):
        return self.execute(
            "delete", uri, body=params, headers=headers, timeout=timeout
        )
