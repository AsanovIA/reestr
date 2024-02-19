from django.urls import include, path

from core.urls import get_path
from database.views import (
    APP_LABEL,
    ModelsView,
)

# def get_path_settings(app_info):
#     return [
#         path(f'{app_info}/', ModelView.as_view(app_label=app_info), name=app_info),
#         path(f'{app_info}/', include(get_path_model(app_info))),
#     ]

# urlpatterns = [
#     path('settings/', include([
#         path('', ModelsView.as_view(), name='settings'),
#         path('', include(get_path_settings(app_info))),
#     ])),
# ]

# def get_path_settings(APP_LABEL):
#     return [
#         path(f'{APP_LABEL}/', MainListView.as_view(app_label=APP_LABEL), name=APP_LABEL),
#         path(f'{APP_LABEL}/<slug:slug>/', include(get_path(APP_LABEL))),
#     ]


urlpatterns = [
    path('settings/', include([
        path('', ModelsView.as_view(), name='settings'),
        path('', include(get_path(APP_LABEL))),
        # path('', include(get_path_settings(APP_LABEL))),
    ])),
]
