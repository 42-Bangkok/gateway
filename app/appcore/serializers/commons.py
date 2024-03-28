from ninja import Schema


class ErrorResponse(Schema):
    code: str
    detail: str
