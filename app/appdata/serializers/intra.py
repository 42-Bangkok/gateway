import datetime
from typing import Literal
from ninja import Schema


class CadetStatusGetOut(Schema):
    updated: datetime.datetime
    blackholed: bool
    enrollment: Literal["cadet", "pisciner", "no-cursus"]
