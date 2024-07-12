from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError

from .models import User
from .schemas import UserIn, UserOut
from .constants import NEGATIVE_AUTO_POST_REPLY_ERROR


@api_controller
class UserController:
    @route.get('/', auth=JWTAuth(), response={200: UserOut})
    def retrieve_user(self, request):
        return request.user

    @route.post('create/', response={201: UserOut})
    def create_user(self, request, data: UserIn):
        if data.get('auto_post_reply') < 0:
            raise HttpError(400, NEGATIVE_AUTO_POST_REPLY_ERROR)

        user = User(username=data.username)
        user.set_password(data.password)
        user.save()
        return user

    @route.patch('update-auto-reply/', auth=JWTAuth())
    def update_auto_reply(self, request, auto_post_reply: int):
        if auto_post_reply < 0:
            raise HttpError(400, NEGATIVE_AUTO_POST_REPLY_ERROR)

        request.user.auto_post_reply = auto_post_reply
        request.user.save()
        return request.user
