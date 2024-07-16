from typing import Optional

from datetime import date
from ninja import Schema, ModelSchema, Field

from user.schemas import UserOutputSchema
from .models import Post, Comment


class PostInputSchema(ModelSchema):
    class Meta:
        model = Post
        fields = ['title', 'content']

class PostOutputSchema(ModelSchema):
    user: UserOutputSchema

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at']

class PostUpdateSchema(Schema):
    title: Optional[str]
    content: Optional[str]

class CommentInputSchema(ModelSchema):
    class Meta:
        model = Comment
        fields = ['content']

class CommentOutputSchema(ModelSchema):
    post_id: int = Field(..., alias='post.id')
    user: UserOutputSchema
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at']

class CommentDailyBrekadownSchema(Schema):
    day: date
    total_comments: int
    blocked_comments: int
    published_comments: int
