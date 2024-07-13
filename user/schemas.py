from typing import Optional
from ninja import Schema


class UserInputSchema(Schema):
    username: str
    password: str
    auto_post_reply: Optional[int]

class UserOutputSchema(Schema):
    id: int
    username: str
    auto_post_reply: Optional[int]
