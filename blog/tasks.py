from ai_blog.celery import celery_app

from user.models import User

from .models import Comment, CommentResponse
from .helpers import get_ai_response


@celery_app.task(name='blog.tasks.auto_comment_response')
def auto_comment_response(user_id=None, comment_id=None):
    try:
        comment = Comment.objects.get(id=comment_id)
        user = User.objects.get(id=user_id)
    except (Comment.DoesNotExist, User.DoesNotExist):
        return
    
    response = Comment.objects.create(
        content = get_ai_response(comment.content),
        post = comment.post,
        user = user,
        generated_by_ai = True,
        is_response = True
    )
    comment.task.crontab.delete()
    
    CommentResponse.objects.create(comment=comment, response=response)
