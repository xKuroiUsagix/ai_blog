from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from .models import User
from .schemas import UserIn, UserOut


@api_controller
class UserController:
    @route.get('/', response={200: UserOut}, auth=JWTAuth())
    def retrieve_user(self, request):
        return request.user

    @route.post('create/', response={201: UserOut})
    def create_user(self, request, data: UserIn):
        user = User(username=data.username)
        user.set_password(data.password)
        user.save()
        return user
