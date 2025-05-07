from marshmallow import ValidationError

from nhmail.constants import LAMBDA_URI, ENDPOINT_FOR_SEND_EMAIL, LAMBDA_AUTHEN
from nhmail.client import ServiceHttpClient
from nhmail.validators import SendEmailSchema

HEADERS = {
    "Authorization": LAMBDA_AUTHEN,
    "Content-Type": "application/json",
}


class MailWrapSystem:
    def __init__(self, **kwargs):
        self.body = kwargs.get("body")

    def send_verify_password(self):
        try:
            SendEmailSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(base_url=LAMBDA_URI).execute(
            method="post",
            uri=ENDPOINT_FOR_SEND_EMAIL,
            body=self.body,
            headers=HEADERS,
        )

        return response

    def send_welcome(self):
        try:
            SendEmailSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(base_url=LAMBDA_URI).execute(
            method="post",
            uri=ENDPOINT_FOR_SEND_EMAIL,
            body=self.body,
            headers=HEADERS,
        )
        return response

    def send_staff_confirm(self):
        try:
            SendEmailSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(base_url=LAMBDA_URI).execute(
            method="post",
            uri=ENDPOINT_FOR_SEND_EMAIL,
            body=self.body,
            headers=HEADERS,
        )

        return response

    def send_custom_body(self):
        response = ServiceHttpClient(base_url=LAMBDA_URI).execute(
            method="post",
            uri=ENDPOINT_FOR_SEND_EMAIL,
            body=self.body,
            headers=HEADERS,
        )

        return response
