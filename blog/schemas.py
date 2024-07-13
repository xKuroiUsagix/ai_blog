from datetime import datetime
from ninja import Schema, Field

from user.schemas import UserOutputSchema


class PostInputSchema(Schema):
    title: str
    content: str

class PostOutputSchema(Schema):
    id: int
    title: str
    content: str
    user: UserOutputSchema
    created_at: datetime

class CommentInputSchema(Schema):
    content: str
    post_id: int

class CommentOutputSchema(Schema):
    id: int
    content: str
    post_id: int = Field(None, alias='id')
    user: UserOutputSchema
    created_at: datetime

class CommentResponseSchema(Schema):
    reply_to: int
    content: str
    post_id: int
