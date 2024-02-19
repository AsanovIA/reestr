from django.urls import path, include

from account.views import (
    APP_LABEL,
    UserPasswordChangeView,
    UserLoginView,
    logout_user, AccountSettingsView,
)

urlpatterns = [
    path(f'{APP_LABEL}/', include([
        path('settings/', AccountSettingsView.as_view(),
             name='account_settings'),
        path('login/', UserLoginView.as_view(), name='login'),
        path('logout/', logout_user, name='logout'),
        path("password_change/", UserPasswordChangeView.as_view(),
             name="password_change"),
    ]))
]
