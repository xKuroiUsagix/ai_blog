from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth
from pydantic import PositiveInt
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK

from .models import User
from .schemas import UserInputSchema, UserOutputSchema


@api_controller('/user')
class UserController:
    @route.get('/', auth=JWTAuth(), response={HTTP_200_OK: UserOutputSchema})
    def retrieve_user(self, request):
        return request.user

    @route.post('/create', response={HTTP_201_CREATED: UserOutputSchema})
    def create_user(self, request, data: UserInputSchema):
        user = User(username=data.username)
        user.set_password(data.password)
        user.save()
        return user

    @route.patch('/update-auto-reply', auth=JWTAuth(), response={HTTP_200_OK: UserOutputSchema})
    def update_auto_reply(self, request, auto_post_reply: PositiveInt):
        request.user.auto_post_reply = auto_post_reply
        request.user.save()
        return request.user
