from typing import Optional
from ninja import Schema


class UserIn(Schema):
    username: str
    password: str
    auto_post_reply: Optional[int]

class UserOut(Schema):
    id: int
    username: str
    auto_post_reply: Optional[int]
