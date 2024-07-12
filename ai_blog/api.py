from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from user.api import UserController


api = NinjaExtraAPI()
api.register_controllers(
    NinjaJWTDefaultController,
    UserController,
)
