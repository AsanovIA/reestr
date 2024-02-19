from django.apps import apps
from django.http import Http404
from django.views.generic.base import TemplateView

from core.mixins import (
    BaseSiteMixin, MultipleListView,
    ChangeFormView, AddFormView, DeleteFormView, HistoryListView,
)
from core.utils import (
    has_permission_add,
    get_slug_url,
    get_model_perms,
    SETTINGS_APP_LIST, try_get_url,
)
from database.forms import (
    PostForm, DivisionForm, SubDivisionForm, ConditionContractForm,
    StatusContractForm, DepartmentForm, ClientForm, StageBeginNameForm,
    StageMiddleNameForm, StageEndNameForm
)

APP_LABEL = 'database'

settings_dict = {
    'post': {
        # 'fields_related': (),
        'fields_display': PostForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('abbr', 'view',),
        # 'readonly_fields': (),
    },
    'division': {
        # 'fields_related': (),
        'fields_display': DivisionForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'subdivision': {
        'fields_related': ('division',),
        'fields_display': SubDivisionForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'conditioncontract': {
        # 'fields_related': (),
        'fields_display': ConditionContractForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'statuscontract': {
        # 'fields_related': (),
        'fields_display': StatusContractForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    # 'controlprice': {
    #     # 'fields_related': (),
    #     'fields_display': ControlPriceForm.Meta.fields,
    #     'fields_link': ('name',),
    #     # 'fields_editable': ('view',),
    #     # 'readonly_fields': (),
    # },
    'department': {
        # 'fields_related': (),
        'fields_display': DepartmentForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'client': {
        'fields_related': ('department',),
        'fields_display': ClientForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'stagebeginname': {
        'fields_related': (),
        'fields_display': StageBeginNameForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'stagemiddlename': {
        'fields_related': (),
        'fields_display': StageMiddleNameForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'stageendname': {
        'fields_related': (),
        'fields_display': StageEndNameForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'employee': {
        'fields_related': ('post', 'division'),
        'fields_display': (
            '__str__', 'tabel', 'norma', 'post', 'division', 'view',
        ),
        'fields_link': ('__str__',),
        'fields_editable': (),
        'readonly_fields': (),
    },
}


# =============== Форма базы данных ================
class SettingsMixin:
    """миксин формирование списка моделей БД"""

    sidebar = 'menu_sidebar'

    def get_sidebar_list(self):
        return SETTINGS_APP_LIST

    def construct_index_list(self, label=None):
        """Список моделей для заглавной страницы БД и боковой панели БД"""

        request = self.request
        app_list = []
        settings_app_list = self.get_sidebar_list()
        if label:
            settings_app_list = [label]

        for app_label in settings_app_list:
            has_module_perms = request.user.has_module_perms(app_label)
            if not has_module_perms:
                continue

            urlargs = {'current_app': app_label}
            models_app = apps.get_app_config(app_label).get_models()
            model_list = []
            for model in models_app:
                opts = model._meta
                perms = get_model_perms(request, model)
                if True not in perms.values():
                    continue

                model_dict = {
                    'name': opts.model_name,
                    'vnp': opts.verbose_name_plural,
                    'perms': perms,
                    'add_url': None,
                    'list_url': None,
                }
                urlargs.update({'slug': get_slug_url({}, opts.model_name)})
                model_dict["list_url"] = try_get_url(
                    f'{app_label}_list', **urlargs
                )
                if has_permission_add(request, model):
                    model_dict["add_url"] = try_get_url(
                        f'{app_label}_add', **urlargs
                    )

                model_list.append(model_dict)
            model_list.sort(key=lambda x: x["vnp"].lower())

            app_dict = {
                "name": apps.get_app_config(app_label).verbose_name,
                "app_label": app_label,
                "app_url": try_get_url(app_label, current_app=app_label),
                "models": model_list,
            }
            app_list.append(app_dict)

        return app_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Настройки'
        context['app_list'] = self.construct_index_list()
        return context


class ModelsView(SettingsMixin, BaseSiteMixin, TemplateView):
    """Список всех моделей БД"""

    template_name = 'database/index.html'
    sidebar = None

    def get(self, request, *args, **kwargs):
        if not any(
                request.user.has_module_perms(app_label)
                for app_label in SETTINGS_APP_LIST
        ):
            raise Http404

        return super().get(request, *args, **kwargs)


# class ModelView(ModelsView):
#     """Список моделей раздела БД"""
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['app_list'] = self.get_app_list(self.app_label)
#         return context


class MainListView(ModelsView):
    """Список моделей раздела БД"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_list'] = self.construct_index_list(self.app_label)
        return context


class ObjectListView(SettingsMixin, MultipleListView):
    """Список моделей"""


class ObjectChangeView(SettingsMixin, ChangeFormView):
    """Изменения форм"""


class ObjectAddView(SettingsMixin, AddFormView):
    """Добавления форм"""


class ObjectDeleteView(SettingsMixin, DeleteFormView):
    """Удаление форм"""


class ObjectHistoryView(SettingsMixin, HistoryListView):
    """История изменений объекта"""
