from typing import List

from ninja_extra import api_controller, route, permissions
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN
)

from .models import Post, Comment, CommentResponse
from .schemas import (
    PostInputSchema, 
    PostOutputSchema,
    PostUpdateSchema,
    CommentOutputSchema, 
    CommentInputSchema,
)
from .helpers import ai_verify_safety
from .constants import (
    HARMFUL_CONTENT_ERROR, BLOCKED_COMMENT_ERROR, WRONG_USER_POST_ERROR, 
    WRONG_USER_COMMENT_ERROR, POST_UPDATE_NO_FIELDS_ERROR
)


@api_controller('/blog', auth=JWTAuth(), permissions=[permissions.IsAuthenticated])
class BlogController:
    @route.get('/post/{post_id}', response={HTTP_200_OK: PostOutputSchema})
    def retrieve_post(self, request, post_id: int):
        return get_object_or_404(Post, id=post_id)

    @route.get('/post-list', response={HTTP_200_OK: List[PostOutputSchema]})
    def retrieve_all_posts(self, request):
        return Post.objects.all()

    @route.get('/user/{username}/posts', response={HTTP_200_OK: List[PostOutputSchema]})
    def retrieve_user_posts(self, request, username: str):
        return Post.objects.filter(user__username=username).order_by('-created_at')
    
    @route.get('/post/{post_id}/comments', response={HTTP_200_OK: List[CommentOutputSchema]})
    def retrieve_post_comments(self, request, post_id: int):
        post = get_object_or_404(Post, id=post_id)
        return post.comment.all().exclude(Q(is_response=True) | Q(is_blocked=True)).order_by('-created_at')

    @route.post('/create-post', response={HTTP_201_CREATED: PostOutputSchema})
    def create_post(self, request, data: PostInputSchema):
        if not ai_verify_safety(data.content):
            raise HttpError(HTTP_400_BAD_REQUEST, HARMFUL_CONTENT_ERROR)

        return Post.objects.create(
            user = request.user,
            title = data.title,
            content = data.content
        )

    @route.patch('/post/{post_id}/update', response={HTTP_200_OK: PostOutputSchema})
    def update_post(self, request, post_id: int, data: PostUpdateSchema):
        if data.title is None and data.content is None:
            raise HttpError(HTTP_400_BAD_REQUEST, POST_UPDATE_NO_FIELDS_ERROR)

        if data.content:
            if not ai_verify_safety(data.content):
                raise HttpError(HTTP_400_BAD_REQUEST, HARMFUL_CONTENT_ERROR)

        post = get_object_or_404(Post, id=post_id)
        
        if data.title:
            post.title = data.title
        if data.content:
            post.content = data.content

        post.save()

        return post

    @route.delete('/post/{post_id}/delete')
    def delete_post(self, request, post_id: int):
        post = get_object_or_404(Post, id=post_id)

        if post.user != request.user:
            return HttpError(HTTP_403_FORBIDDEN, WRONG_USER_POST_ERROR)

        post.delete()
        return HTTP_204_NO_CONTENT

    @route.get('/comment/{comment_id}', response={HTTP_200_OK: CommentOutputSchema})
    def retrieve_comment(self, request, comment_id: int):
        comment = get_object_or_404(Comment, id=comment_id)
        
        if comment.is_blocked:
            raise HttpError(HTTP_400_BAD_REQUEST, BLOCKED_COMMENT_ERROR)
        return comment

    @route.post('/post/{post_id}/create-comment', response={HTTP_201_CREATED: CommentOutputSchema})
    def create_comment(self, request, post_id: int, data: CommentInputSchema):
        is_blocked = not ai_verify_safety(data.content)
        comment = self._create_comment(request.user, data, post_id=post_id, is_blocked=is_blocked)

        if is_blocked:
            raise HttpError(HTTP_400_BAD_REQUEST, HARMFUL_CONTENT_ERROR)
        return comment

    @route.post('post/{post_id}/comment/{comment_id}/reply', response={HTTP_201_CREATED: CommentOutputSchema})
    def reply_to_comment(self, request, post_id: int, comment_id: int, data: CommentInputSchema):
        is_blocked = not ai_verify_safety(data.content)
        comment = get_object_or_404(Comment, id=comment_id)
        response = self._create_comment(request.user, data, post_id=post_id, is_response=True, is_blocked=is_blocked)
        CommentResponse.objects.create(comment=comment, response=response)

        if is_blocked:
            raise HttpError(HTTP_400_BAD_REQUEST, HARMFUL_CONTENT_ERROR)
        return response

    @route.delete('post/{post_id}/comment/{comment_id}')
    def delete_comment(self, request, post_id: int, comment_id: int):
        comment = get_object_or_404(Comment, id=comment_id)
        post = get_object_or_404(Post, id=post_id)

        if comment.user != request.user and post.user != request.user:
            raise HttpError(HTTP_403_FORBIDDEN, WRONG_USER_COMMENT_ERROR)

        comment.delete()
        return HTTP_204_NO_CONTENT

    def _create_comment(self, user, data: CommentInputSchema, post_id, **kwargs):
        return Comment.objects.create(
            user = user,
            post = get_object_or_404(Post, id=post_id),
            content = data.content,
            **kwargs
        )
