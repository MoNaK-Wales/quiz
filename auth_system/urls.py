from django.urls import path
from auth_system.views import *

app_name = 'auth'

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
]
