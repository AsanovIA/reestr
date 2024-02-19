from django.urls import path, include

from core.urls import get_path
from users.views import APP_LABEL, UserPasswordSetView

urlpatterns = [
    # path('settings/', include(get_path_settings(APP_LABEL))),
    path('settings/', include([
        path('', include(get_path(APP_LABEL))),
        path(
            f"{APP_LABEL}/<slug:slug>/password/",
            UserPasswordSetView.as_view(),
            name="password_set"
        ),
    ])),
]
