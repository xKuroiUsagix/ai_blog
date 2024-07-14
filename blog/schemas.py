from typing import Optional

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

class PostUpdateSchema(Schema):
    title: Optional[str]
    content: Optional[str]

class CommentInputSchema(Schema):
    content: str

class CommentOutputSchema(Schema):
    id: int
    content: str
    post_id: int = Field(None, alias='id')
    user: UserOutputSchema
    created_at: datetime
