from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    customer_id = fields.Str(required=False, allow_none=True)
    email = fields.Email(required=True)
    name = fields.Str(required=True)
    role = fields.Str(required=False, allow_none=True)
    status = fields.Str(required=False, allow_none=True)
    invitation_token = fields.Str(required=False, allow_none=True)
    last_login_at = fields.DateTime(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    password = fields.Str(load_only=True, required=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
