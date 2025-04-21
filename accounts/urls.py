from django.urls import path, include
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("profile_login/", views.user_login, name="profile_login"),
    path("profile/", views.profile_view, name="profile"),
    path("user_logout/", views.user_logout, name="user_logout"),
    path("activate/<str:uidb64>/<str:token>/", views.activate, name="activate"),
    path("activation-email/", views.activation_email, name="activation_email"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path(
        "activate/intermediate/",
        views.activate_intermediate,
        name="activate_intermediate",
    ),
    path("activate/", views.activate, name="activate"),
    path("login/", views.user_login, name="login"),
    path("accounts/", include("allauth.urls")),  
]
