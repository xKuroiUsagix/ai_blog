from ninja import ModelSchema

from .models import User


class UserInputSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['username', 'password']

class UserOutputSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username', 'auto_post_reply']
