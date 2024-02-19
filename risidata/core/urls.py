import importlib

from django.apps import apps
from django.urls import path


def get_path(app_label, default_actions=None):
    urls = []
    actions = ['list', 'add', 'change', 'delete', 'history']
    if default_actions is not None:
        actions = [default_actions]

    def get_class_action(module, name):
        try:
            return getattr(module.views, name)
        except AttributeError:
            return None

    app_config = apps.get_app_config(app_label)
    app_module = getattr(
        app_config, 'module', None
    ) or importlib.import_module(app_label)

    class_name = 'MainListView'
    class_action = get_class_action(app_module, class_name)

    if class_action is None and app_label == 'users':
        app_config_database = apps.get_app_config('database')
        app_module_database = getattr(
            app_config_database, 'module', None
        ) or importlib.import_module(app_label)
        class_action = get_class_action(app_module_database, class_name)

    if class_action is not None:
        urls.append(
            path(
                f'{app_label}/',
                class_action.as_view(app_label=app_label),
                name=app_label,
            )
        )

    for action in actions:
        class_name = f'Object{action.capitalize()}View'
        class_action = get_class_action(app_module, class_name)
        if class_action is None and app_label == 'users':
            class_action = get_class_action(app_module_database, class_name)
        if class_action is None:
            continue

        name_url = (app_label, action.lower())
        url_path = f'{app_label}/<slug:slug>/'
        if action == 'list':
            url_path += ''
        else:
            url_path += f'{action}/'

        urls.append(
            path(
                url_path,
                class_action.as_view(app_label=app_label),
                name='%s_%s' % name_url
            )
        )

    return urls
