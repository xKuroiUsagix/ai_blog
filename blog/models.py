import json
from datetime import timedelta

from django.db import models
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from ai_blog.settings import AUTH_USER_MODEL
from .constants import MAX_COMMENT_LENGTH


class Post(models.Model):
    title = models.CharField(max_length=128, db_index=True)
    content = models.TextField()
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.CharField(max_length=MAX_COMMENT_LENGTH)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment')
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    generated_by_ai = models.BooleanField(default=False, db_index=True)
    is_response = models.BooleanField(default=False, db_index=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    respond_at = models.DateTimeField(null=True, blank=True)
    task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)
    
    def _create_crontab_schedule(self, respond_at):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute = respond_at.minute,
            hour = respond_at.hour,
            day_of_week=respond_at.isoweekday(),
            day_of_month=respond_at.day,
            month_of_year=respond_at.month
        )

        return schedule
    
    def _create_task(self):
        return PeriodicTask.objects.create(
            crontab = self._create_crontab_schedule(self.respond_at),
            name = f'Auto comment response. Respond at {self.respond_at}',
            task = 'blog.tasks.auto_comment_response',
            kwargs = json.dumps({'user_id': self.user.id, 'comment_id': self.id}),
            one_off = True
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if (not self.user.auto_post_reply or self.task or self.is_response 
                or self.generated_by_ai or self.is_blocked):
            return

        self.respond_at = self.created_at + timedelta(minutes=self.user.auto_post_reply)
        self.task = self._create_task()
        self.save()
    
    def __str__(self):
        return self.content[:15] + '...'


class CommentResponse(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    response = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='response')
