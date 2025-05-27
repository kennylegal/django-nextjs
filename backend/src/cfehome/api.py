from django.contrib.auth import get_user_model
from helpers.api.auth.controllers import DjangoNextCustomController
from helpers.api.auth.permissions import anon_required, user_or_anon
from helpers.api.auth.schemas import UsernameMandatoryEmailMandatorySchema
from helpers.api.users.schemas import UserSchema
from ninja.errors import HttpError
from ninja_extra import NinjaExtraAPI
from ninja_extra.permissions import AllowAny
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.tokens import RefreshToken

User = get_user_model()

api = NinjaExtraAPI(auth=user_or_anon)

# adds /token/ pair/refresh/
api.register_controllers(DjangoNextCustomController)


@api.get("/hello/", auth=user_or_anon)
def hello(request):
    # print(request)
    return {"message": "Hello World"}


@api.post("/signup/", response=UserSchema, auth=anon_required)
def signup(request, new_user: UsernameMandatoryEmailMandatorySchema):
    try:
        user = User.objects.create_user(
            username=new_user.username,
            email=new_user.email,
            password=new_user.password,
            is_active=True,
        )
        user.save()
        token = RefreshToken.for_user(user)
        return {
            "username": user.username,
            "email": user.email,
            "is_authenticated": True,
            "access_token": str(token.access_token),
            "refresh_token": str(token),
        }
    except Exception as e:
        raise HttpError(500, "Could not create user. Please try again later")
