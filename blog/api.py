from typing import List

from ninja_extra import api_controller, route, permissions
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404

from .models import Post, Comment, CommentResponse
from .schemas import (
    PostInputSchema, 
    PostOutputSchema, 
    CommentOutputSchema, 
    CommentInputSchema,
    CommentResponseSchema
)
from .helpers import ai_verify_safety
from .constants import HARMFUL_CONTENT_ERROR


@api_controller('/blog/post', auth=JWTAuth(), permissions=[permissions.IsAuthenticated])
class PostController:
    @route.get('/', response={200: PostOutputSchema})
    def retrieve_post(self, request, post_id: int):
        return get_object_or_404(Post, id=post_id)

    @route.get('/list', response={200: List[PostOutputSchema]})
    def retrieve_posts_list(self, request):
        return Post.objects.all()

    @route.get('/user/list', response={200: List[PostOutputSchema]})
    def retrieve_user_posts(self, request, username: str):
        return Post.objects.filter(user__username=username).order_by('-created_at')
    
    @route.get('/comments', response={200: List[CommentOutputSchema]})
    def retrieve_post_comments(self, request, post_id: int):
        post = get_object_or_404(Post, id=post_id)
        return post.comment.all().exclude(is_response=True).order_by('-created_at')

    @route.post('/create', response={201: PostOutputSchema})
    def create_post(self, request, data: PostInputSchema):
        if not ai_verify_safety(data.content):
            raise HttpError(400, HARMFUL_CONTENT_ERROR)

        return Post.objects.create(
            user = request.user,
            title = data.title,
            content = data.content
        )

    @route.patch('/update-content', response={200: PostOutputSchema})
    def update_post(self, request, content: str, post_id: int):
        if not ai_verify_safety(content):
            raise HttpError(400, HARMFUL_CONTENT_ERROR)

        post = get_object_or_404(Post, id=post_id)
        post.content = content
        post.save()

        return post


@api_controller('/blog/comment', auth=JWTAuth(), permissions=[permissions.IsAuthenticated])
class CommentController:
    @route.get('/', response={200: CommentOutputSchema})
    def retrieve_comment(self, request, comment_id):
        return get_object_or_404(Comment, id=comment_id)

    @route.post('/create', response={201: CommentOutputSchema})
    def create_comment(self, request, data: CommentInputSchema):
        if not ai_verify_safety(data.content):
            raise HttpError(400, HARMFUL_CONTENT_ERROR)

        return self._create_comment(request.user, data)

    @route.post('/reply', response={201: CommentOutputSchema})
    def reply_to_comment(self, request, data: CommentResponseSchema):
        if not ai_verify_safety(data.content):
            raise HttpError(400, HARMFUL_CONTENT_ERROR)

        comment = get_object_or_404(Comment, id=data.reply_to)
        response = self._create_comment(request.user, data, is_response=True)
        CommentResponse.objects.create(comment=comment, response=response)

        return response

    def _create_comment(self, user, data: CommentInputSchema, **kwargs):
        return Comment.objects.create(
            user = user,
            post = get_object_or_404(Post, id=data.post),
            content = data.content,
            **kwargs
        )