from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI
# from ninja_extra import api_controller, route
# from ninja_jwt.authentication import JWTAuth
from user.api import UserController


api = NinjaExtraAPI()
api.register_controllers(
    NinjaJWTDefaultController,
    UserController
)
