from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth
from pydantic import NonNegativeInt

from .models import User
from .schemas import UserInputSchema, UserOutputSchema


@api_controller('/user')
class UserController:
    @route.get('/', auth=JWTAuth(), response={200: UserOutputSchema})
    def retrieve_user(self, request):
        return request.user

    @route.post('/create', response={201: UserOutputSchema})
    def create_user(self, request, data: UserInputSchema):
        user = User(
            username = data.username,
            auto_post_reply = data.auto_post_reply
        )
        user.set_password(data.password)
        user.save()
        return user

    @route.patch('/update-auto-reply', auth=JWTAuth(), response={200: UserOutputSchema})
    def update_auto_reply(self, request, auto_post_reply: NonNegativeInt):
        request.user.auto_post_reply = auto_post_reply
        request.user.save()
        return request.user
