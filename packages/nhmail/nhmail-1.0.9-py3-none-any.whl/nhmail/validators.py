from marshmallow import Schema, fields, validate


class SendEmailSchema(Schema):
    _email_validator = validate.Email()
    _name_validator = validate.Length(min=1)
    to = fields.Str(required=True, validate=_email_validator)
    template_id = fields.Str(required=True)
    cc_emails = fields.List(fields.String(), missing=[])
    bcc_emails = fields.List(fields.String(), missing=[])
    template_data = fields.Nested(
        {
            "redirect_link": fields.Str(required=True),
            "user_name": fields.Str(required=True, validate=_name_validator),
            "password": fields.Str(required=False),
        },
        required=True,
    )
