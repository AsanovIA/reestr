import importlib
import os
from itertools import chain

from django import forms
from django.apps import apps
from django.contrib.admin.utils import flatten_fieldsets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.db import transaction, router, models
from django.db.models import Q
from django.forms.models import modelform_factory, modelformset_factory
from django.http import HttpResponseRedirect, Http404
from django.urls import NoReverseMatch
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.views.generic import TemplateView, FormView
from django.views.generic.base import ContextMixin

from core.buildform import SiteForm
from core.utils import (
    SETTINGS_APP_LIST,
    get_slug_kwarg, get_slug_url, try_get_url, label_for_field,
    has_permission_add, has_permission_change, has_permission_delete,
    has_permission_view, has_permission_close,
    get_delete_models,
    NestedObjectsContract,
)


def get_main_menu(request):
    menu = []

    home = try_get_url('home', None, 'contract')
    menu.append({'title': 'Проекты', 'url': home})

    slug = get_slug_url({}, 'contract')
    contract = try_get_url('contract_list', slug, 'contract')
    menu.append({'title': 'Договора', 'url': contract})

    slug = get_slug_url({}, 'employee')
    employee = try_get_url('employee_list', slug, 'contract')
    menu.append({'title': 'Сотрудники', 'url': employee})

    slug = get_slug_url({}, 'contract')
    archive = try_get_url('archive_contract_list', slug, 'contract')
    menu.append({'title': 'Архив', 'url': archive})

    for app_label in SETTINGS_APP_LIST:
        has_module_perms = request.user.has_module_perms(app_label)
        if not has_module_perms:
            continue
        settings = try_get_url('settings', current_app='database')
        menu.append({'title': 'Настройки', 'url': settings})
        break

    return menu


class BaseSiteMixin(LoginRequiredMixin, ContextMixin):
    """
    Основной миксин сайта

    dict_models_list = {
        None: {'name': '', 'name_plural': '', 'suffix': '', 'list': []}
    }
        - словарь параметров для нескольких списков на одной странице
        'None' - название списка моделей (используется в GET запросах)
        name - название списка для отображения на дисплее
        name_plural - название списка во множественном числе
        suffix - суффикс
        list - список model_name моделей в формате str
    """

    action = None
    app_label = None
    btn_add = None
    btn_save = True
    dict_models_list = {
        None: {
            'name': '',
            'name_plural': '',
            'suffix': '',
            'list': [],
            'fields': [],
        }
    }
    empty_value_display = '-'
    form_class = None
    initial = {}
    kwargs = {}
    model = None
    model_name = None
    models_list = []
    models_name = None
    media = forms.Media()
    obj_id = None
    object_verbose_name = ''
    opts_dict = {}  # Параметры отображения полей списка
    prefix = None
    related_id = None
    sidebar = None
    success_url = None
    user_perm = {}  # Права пользователя

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.app_label is not None and not self.opts_dict:
            self.build_opts_dict()
            aa = 1

    def build_opts_dict(self):
        app_label = self.app_label
        app_config = apps.get_app_config(app_label)
        app_module = getattr(
            app_config, 'module', None
        ) or importlib.import_module(app_label)
        try:
            self.opts_dict = getattr(app_module.views, 'settings_dict', {})
        except AttributeError:
            pass

    def get_add_url(self, model_name=None):
        app_label = self.app_label
        model_name = (
                model_name
                or self.get_model_name()
                or self.model._meta.model_name
        )
        slug = get_slug_url(self.kwargs, model_name)
        return try_get_url(f'{app_label}_add', slug, app_label)

    def has_o2o(self, model):
        if any(
                (
                        isinstance(field, models.OneToOneField)
                        and not field.primary_key
                )
                for field in model._meta.get_fields()
        ):
            return True
        return False

    def get_success_url(self):
        if self.success_url:
            return str(self.success_url)
        app_label = self.app_label
        model_name = self.model_name
        slug = None

        for key, value in self.dict_models_list.items():
            if model_name in (key, value['list']):
                model_name = key
                slug = get_slug_url(self.kwargs, model_name, obj_id='0')
                break

        if slug is None:
            model = self.get_model(model_name)
            for field in model._meta.get_fields():
                if (
                        isinstance(field, models.OneToOneField)
                        and not field.primary_key
                ):
                    related_model_name = field.related_model._meta.model_name
                    slug = get_slug_url({}, related_model_name)
                    break

        if slug is None:
            slug = get_slug_url(self.kwargs, model_name, obj_id='0')

        return try_get_url(f'{app_label}_list', slug, app_label)

        # if (
        #         self.obj_id != '0' or self.action == 'add'
        #         # self.obj_id != '0' and self.related_id != '0'
        #         # or self.action == 'add' and self.related_id != '0'
        # ):
        #     model_name = self.model_name
        #     for key, value in self.dict_models_list.items():
        #         if model_name in value['list']:
        #             model_name = key
        #             break
        #     slug = get_slug_url(self.kwargs, model_name, obj_id='0')
        #
        #     return try_get_url(f'{app_label}_list', slug, app_label)
        #
        # return reverse_lazy('home')

    def get_model_name(self):
        return get_slug_kwarg(self.kwargs)[0]

    def get_obj_id(self):
        return get_slug_kwarg(self.kwargs)[1]

    def get_related_id(self):
        return get_slug_kwarg(self.kwargs)[2]

    def get_attributes(self):
        (
            self.model_name,
            self.obj_id,
            self.related_id
        ) = get_slug_kwarg(self.kwargs)

    def get_model(self, model_name=None):
        model_name = model_name or self.model_name
        try:
            return apps.get_model(self.app_label, model_name)
        except LookupError:
            for app_configs in apps.get_app_configs():
                app_config = apps.get_app_config(app_configs.label)
                for model in app_config.get_models():
                    if model._meta.model_name == model_name:
                        self.app_label = app_configs.label
                        return model

    def get_attributes_model_list(self):
        self.get_attributes()
        if self.model_name is None and self.model is None:
            raise ImproperlyConfigured('Model not defined.')

        model_name = self.model_name or self.model._meta.model_name
        if model_name and model_name in self.dict_models_list:
            self.models_list = self.dict_models_list[model_name]['list']
            self.models_name = self.dict_models_list[model_name]['name_plural']
        else:
            self.models_list = [model_name]
            if self.model is None and len(self.models_list) == 1:
                self.model = self.get_model()

    def get_attributes_list(self, model_name):
        self.model_name = model_name
        self.model = self.get_model(model_name)
        self.form_changelist = self.get_form_class_model()

    def get_attributes_model(self):
        self.get_attributes()
        if self.model is None:
            self.model = self.get_model()

    def get_initial(self):
        if isinstance(self.initial, dict):
            return self.initial.copy()
        return {}

    def get_prefix(self):
        return self.prefix

    def get_request_kwargs(self):
        if self.request.method in ("POST", "PUT"):
            return {
                "data": self.request.POST.copy(),
                "files": self.request.FILES,
            }
        return {}

    def get_form_kwargs(self, **kwargs):
        """Формирование словаря аргументов для form"""
        if hasattr(super(), 'get_form_kwargs'):
            kwargs.update(**super().get_form_kwargs())
        else:
            kwargs.update(
                {
                    'initial': self.get_initial(),
                    'prefix': self.get_prefix(),
                    **self.get_request_kwargs(),
                }
            )
        if hasattr(self, "object"):
            kwargs.update({"instance": self.object})
        return kwargs

    def get_form_class_model(self, model=None):
        model = model or self.model
        opts = model._meta
        app_module = (
                getattr(opts.app_config, 'module', None)
                or importlib.import_module(opts.app_label)
        )
        form_class_name = model.__name__ + "Form"
        try:
            form_class = getattr(app_module.forms, form_class_name, None)
        except AttributeError:
            form_class = None

        return form_class

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        self.form_class = form_class = self.get_form_class_model()
        if not form_class:
            fields = self.opts_dict.get(self.model_name, {}).get(
                'fields_display'
            )
            form_class = modelform_factory(self.model, fields=fields)
        return form_class

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs(**kwargs))

    def get_readonly_fields(self, form=None):
        if form and hasattr(form, 'Meta'):
            return getattr(form.Meta, 'readonly_fields', ())
        return self.opts_dict.get(self.model_name, {}).get(
            'readonly_fields', ()
        )

    def get_fields(self, form=None):
        try:
            return form.Meta.fields
        except AttributeError:
            if hasattr(self, 'fields') and self.fields != '__all__':
                return self.fields

    def get_fieldsets(self, form):
        try:
            return form.Meta.fieldsets
        except AttributeError:
            return [(None, {"fields": self.get_fields(form)})]

    def get_site_form(self, form):
        fieldsets = self.get_fieldsets(form=form)
        if (
                self.action != 'add' and not self.user_perm.get('change')
                or self.action == 'view'
        ):
            readonly_fields = flatten_fieldsets(fieldsets)
        else:
            readonly_fields = self.get_readonly_fields(form=form)
        return SiteForm(
            form,
            list(fieldsets),
            {},
            readonly_fields,
            model_admin=self,
        )

    def get_empty_value_display(self):
        """Возвращает значение если поле 'только для чтения' пустое"""
        return mark_safe(self.empty_value_display)

    def get_context_data(self, **kwargs):
        kwargs["btn"] = {}
        context = super().get_context_data(**kwargs)
        context['main_menu'] = get_main_menu(self.request)
        context['sidebar'] = self.sidebar
        context['account_settings_url'] = try_get_url(
            name='account_settings', current_app='account'
        )
        if self.object_verbose_name:
            context['object_verbose_name'] = self.object_verbose_name

        return context

    def action_pre_save(self, obj, form, *args, **kwargs):
        if self.request.FILES:
            old_file = form.initial.get('file')
            new_file = form.cleaned_data.get('file')
            if old_file and old_file != new_file:
                os.remove(old_file.path)
                old_file.delete()
                obj.file = new_file

    def get_content_type_for_model(self, obj):
        from django.contrib.contenttypes.models import ContentType

        return ContentType.objects.get_for_model(obj, for_concrete_model=False)

    def log_entry(self, request, obj, message=''):
        """Запись сообщения в журнал изменений"""

        if self.action == 'change' and not message:
            return None

        from risi.models import (
            ADDITION, CHANGE, DELETION, CLOSING, LogEntrySite
        )

        action_flag = {
            'add': ADDITION,
            'change': CHANGE,
            'delete': DELETION,
            'close': CLOSING
        }

        return LogEntrySite.objects.log_action(
            user_id=request.user.pk,
            content_type_id=self.get_content_type_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=str(obj),
            action_flag=action_flag[self.action],
            change_message=message,
        )

    def construct_message(self, form, formsets=None, add=False):
        """Возвращает сообщение об изменениях"""
        from django.contrib.admin.utils import construct_change_message

        return construct_change_message(form, formsets, add)

    def log_change(self, obj, form, add=False):
        """Формирование и запись сообщения об изменениях в журнал"""
        if not add:
            add = self.action == 'add'
        change_message = self.construct_message(form, add=add)
        self.log_entry(self.request, obj, change_message)

    def get_success_message(self, obj):
        action = {'add': 'добавлен', 'change': 'изменен', 'delete': 'удален'}
        name_str = str(obj)
        resume_text = ''
        link_or_text = name_str
        if "_continue" in self.request.POST:
            resume_text = ' Можете продолжить редактирование.'
        else:
            if self.action != 'delete':
                obj_url = obj.get_absolute_url()
                link_or_text = format_html(
                    '<a href="{}">{}</a>', obj_url, name_str
                )

        message = format_html(
            '{} {} успешно {}{}.{}',
            obj._meta.verbose_name,
            link_or_text,
            action[self.action],
            obj.name_suffix,
            resume_text,
        )

        return message

    def message_user_success(self, request, message=''):
        from django.contrib import messages

        messages.success(request, message)

    def message_user_warning(self, request, message=''):
        from django.contrib import messages
        from core.utils import DEFAULT_MESSAGE_WARNING

        message = message or DEFAULT_MESSAGE_WARNING
        # 'Изменения отсутствуют. Сохранение отменено.'
        # 'Сохранение отменено.'
        messages.warning(request, message)

    def get_model_list_perms(self, request, model_list):
        try:
            model_list = [
                self.get_model(model_name) for model_name in model_list
            ]
        except AttributeError:
            pass
        return {
            "add": all(
                has_permission_add(request, model) for model in model_list
            ),
            "change": all(
                has_permission_change(request, model) for model in model_list
            ),
            "delete": all(
                has_permission_delete(request, model) for model in model_list
            ),
            "view": all(
                has_permission_view(request, model) for model in model_list
            ),
            "close": all(
                has_permission_close(request, model) for model in model_list
            ),
        }


class DataObjectMixin(BaseSiteMixin):
    """Миксин действий с объектом формы"""

    template_name = 'core/change_form.html'

    def get_object(self):
        if self.action == 'add':
            return None
        queryset = self.get_queryset()
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model_name
        context['action'] = self.action

        return context

    def get_queryset(self, query=Q()):
        if not query:
            query = Q(('pk', self.obj_id), )
        if self.model:
            return self.model._default_manager.filter(query)
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
            )

    def get(self, request, *args, **kwargs):
        self.get_attributes_model_list()
        self.user_perm = self.get_model_list_perms(request, self.models_list)

        if self.action == 'add':
            if not self.user_perm.get('add'):
                raise Http404
        else:
            if not self.user_perm.get('view'):
                raise Http404
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        self.kwargs.update(action=self.action, current_app=self.app_label)

        return super().get(request, *args, **kwargs)


class DataFormMixin(DataObjectMixin):
    """Миксин обработки формы"""

    @property
    def fields(self):
        if self.form_class:
            fields = None
        else:
            fields = self.opts_dict.get(self.model_name, {}).get(
                'fields_display'
            )
            if not fields:
                raise ImproperlyConfigured(
                    "Using  DataFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited. "
                    "Specify 'fields_display' or create a form." %
                    self.__class__.__name__
                )
        return fields

    def get_delete_url(self, obj):
        app_label = self.app_label
        slug = get_slug_url(self.kwargs, obj_id=obj.pk)
        return try_get_url(f'{app_label}_delete', slug, app_label)

    def get_history_url(self, obj):
        app_label = self.app_label
        urlargs = {
            **self.kwargs,
            'slug': get_slug_url(self.kwargs, obj_id=obj.pk),
        }
        return try_get_url(f'{app_label}_history', **urlargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get('form') or self.get_form()
        site_form = self.get_site_form(form)
        context['siteform'] = site_form
        context['media'] = self.media + site_form.media
        if self.user_perm.get('change') and self.btn_save:
            context['btn']['btn_save'] = True
            context['btn']['btn_save_and_continue'] = True

        if self.action == 'change':
            delete_models = get_delete_models()
            if self.model in delete_models and self.user_perm.get('delete'):
                # пользователь имеет права удаления записи модели
                context['perm_delete'] = True
                context['btn']['btn_delete'] = True
                context['delete_url'] = self.get_delete_url(self.object)

        if 'btn' in context and self.object:
            from risi.models import LogEntrySite

            context['object_verbose_name'] = self.model._meta.verbose_name
            if (
                    self.action != 'add'
                    and has_permission_view(self.request, LogEntrySite)
            ):
                context['btn']['history'] = True
                context['history_url'] = self.get_history_url(self.object)

        return context

    def get_last_change(self, form):
        text = []
        add_msg = '{}: добавлено: {}'
        change_msg = '{}: было: {} стало: {}'
        for field_name in form.changed_data:
            label = label_for_field(field_name, self.model, form)
            new_value = form.cleaned_data[field_name]
            if self.action == 'change':
                f = self.model._meta.get_field(field_name)
                if isinstance(f.remote_field, models.ManyToManyRel):
                    old_value = [item for item in form.initial[field_name]]
                    add_value = set(new_value) - set(old_value)
                    delete_value = set(old_value) - set(new_value)

                    if add_value and delete_value:
                        text.append(f'{label}: добавлено: {add_value} '
                                    f'убрано: {delete_value}')
                    elif add_value:
                        text.append(f'{label}: добавлено: {add_value}')
                    elif delete_value:
                        text.append(f'{label}: убрано: {delete_value}')

                elif isinstance(f.remote_field, models.ManyToOneRel):
                    if isinstance(form.initial[field_name], int):
                        old_value = f.related_model._meta.model.objects.get(
                            pk=form.initial[field_name]
                        )
                        text.append(
                            change_msg.format(label, old_value, new_value)
                        )
                    else:
                        text.append(add_msg.format(label, new_value))
                else:
                    old_value = form.initial.get(field_name)
                    text.append(change_msg.format(label, old_value, new_value))
            else:
                text.append(add_msg.format(label, new_value))

        return '\n'.join(text)

    def form_valid(self, form):
        request = self.request
        if form.has_changed():
            obj = form.save(commit=False)
            # Добавляем дополнительные сведения
            self.action_pre_save(obj, form)
            # Сохраняем обновленный объект
            obj.save()
            form.save_m2m()

            # Запись в журнал
            self.log_change(obj, form)

            # Формирование сообщения об успешной записи
            success_message = self.get_success_message(obj)
            self.message_user_success(request, success_message)
        else:
            self.message_user_warning(request)

        if "_continue" in request.POST:
            return HttpResponseRedirect(request.get_full_path())
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.get_attributes_model_list()
        self.user_perm = self.get_model_list_perms(request, self.models_list)

        if self.action != 'add' and not self.user_perm.get('change'):
            raise Http404
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        self.kwargs.update(action=self.action, current_app=self.app_label)

        return super().post(request, *args, **kwargs)


class MultipleListMixin(BaseSiteMixin):
    """Несколько списков на одной странице."""

    btn_add = True
    formset_initial = []
    list_formset = False
    ordering = None
    page_kwarg = "page"
    paginate_by = None
    paginator_class = Paginator
    template_name = 'core/change_list.html'

    def get_ordering(self):
        return self.ordering

    def get_paginate_by(self):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_paginator(
        self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs
    ):
        """Return an instance of the paginator for this view."""
        return self.paginator_class(
            queryset,
            per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            **kwargs,
        )

    def get_fields_editable(self):
        return self.opts_dict.get(self.model_name, {}).get(
            'fields_editable', ''
        )

    def get_formset_initial(self):
        if isinstance(self.formset_initial, list):
            return self.formset_initial.copy()
        return []

    def get_formset_kwargs(self, **kwargs):
        """Формирование словаря аргументов для formsets"""
        kwargs = {
            'initial': self.get_formset_initial(),
            **kwargs,
            **self.get_request_kwargs(),
        }
        return kwargs

    def get_formset(self, **kwargs):
        FormSet = self.construct_formset()
        return FormSet(**self.get_formset_kwargs(**kwargs))

    def construct_formset(self, extra=0, **kwargs):
        """Создание класса формы для formsets"""
        defaults = {
            'fields': self.get_fields_editable(),
            'widgets': getattr(self.form_changelist.Meta, 'widgets', None),
            **kwargs,
        }
        if not extra:
            extra = len(self.get_formset_initial())
        return modelformset_factory(self.model, extra=extra, **defaults)

    def get_changelist(self):
        from core.utils import ChangeList

        return ChangeList

    def get_fields_for_changelist(self, model_name=None):
        model_name = model_name or self.model_name
        fields_display = self.opts_dict.get(model_name, {}).get(
            'fields_display'
        )
        fields_link = self.opts_dict.get(model_name, {}).get(
            'fields_link', ''
        )

        if not fields_display:
            fields_display = ('id',)
        elif fields_display == '__all__' or fields_display == ('__all__',):
            raise ImproperlyConfigured(
                '"__all__" is not allowed, specify specific fields.')

        if fields_link:
            fields_link_check = fields_link
        elif fields_link is None:
            fields_link_check = ()
        else:
            fields_link = fields_link_check = list(fields_display)[:1]

        fields_editable = self.opts_dict.get(model_name, {}).get(
            'fields_editable', ''
        )

        # Проверка заданных параметров полей
        fields_raise = [
            field
            for field in chain(fields_link_check, fields_editable)
            if field not in fields_display
        ]
        if fields_raise:
            fields_raise = ', '.join(fields_raise)
            raise ImproperlyConfigured(
                f'Missing fields ({fields_raise}) in "fields_display" for'
                f' {self.model.__name__}'
            )

        return fields_display, fields_link, fields_editable

    def get_changelist_instance(self, formset=None, **kwargs):
        """Формирование списка"""

        ChangeList = self.get_changelist()
        (fields_display,
         fields_link,
         fields_editable) = self.get_fields_for_changelist()
        object_list = kwargs.get('queryset')
        cl = ChangeList(
            self.request,
            object_list,
            self,
            self.model,
            self.form_changelist,
            fields_display,
            fields_link,
            fields_editable,
        )
        if cl.fields_editable:
            """Формирование редактируемых полей в списке, если требуется"""
            self.list_formset = True
            if formset is None:
                formset = self.get_formset(**kwargs)
            cl.formset = formset

        return cl

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media = forms.Media()
        cls, errors = [], []
        context['total_result_count'] = 0
        for index, model_name in enumerate(self.models_list):
            self.get_attributes_list(model_name)
            default = {
                'queryset': self.get_queryset(),
                'prefix': f'table-{index}-form'
            }
            if self.request.method == "POST":
                formset = kwargs['formsets'][index]
                default.update(formset=formset)
            cl = self.get_changelist_instance(**default)
            cls.append(cl)
            if cl.formset is not None:
                media += cl.formset.media
                errors += cl.formset.errors
            context['total_result_count'] += cl.result_count
        context['cls'] = cls
        context['errors'] = errors
        context['list_formset'] = self.list_formset
        context['media'] = media + self.media

        if (
                self.list_formset
                and self.user_perm.get('change')
                and self.btn_save
        ):
            context['btn']['btn_save'] = True
            # context['btn']['btn_save_and_continue'] = True

        if self.user_perm.get('add') and self.btn_add:
            context['perm_add'] = True
            context['btn']['btn_add'] = True
            context['add_url'] = self.get_add_url()

        if len(self.models_list) == 1:
            context['object_verbose_name'] = self.model._meta.verbose_name
            context['title'] = self.model._meta.verbose_name_plural
        else:
            context['object_verbose_name'] = self.models_name
            context['title'] = self.models_name

        return context

    def get_queryset(self, query=Q(), model=None):
        model = model if model is not None else self.model
        if not model:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    "cls": self.__class__.__name__
                }
            )
        fields_related = self.opts_dict.get(
            model._meta.model_name, {}
        ).get('fields_related') or (None,)
        queryset = model._default_manager.filter(query).select_related(
            *fields_related
        )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_success_url(self):
        return self.request.get_full_path()

    def formsets_valid(self, request, formsets, *args, **kwargs):
        changecount = 0
        for formset in formsets:
            with transaction.atomic(using=router.db_for_write(self.model)):
                for form in formset.forms:
                    if form.has_changed():
                        obj = form.save(commit=False)
                        # Добавляем дополнительные сведения
                        self.action_pre_save(obj, form, *args, **kwargs)
                        obj.save()
                        form.save_m2m()
                        self.log_change(obj, form)
                        changecount += 1
        if changecount:
            # Формирование сообщения об успешной записи
            success_message = ("%(name)s в количестве %(count)s были успешно "
                               "изменены.") % {
                                  "count": changecount,
                                  "name": self.model._meta.verbose_name_plural,
                              }
            self.message_user_success(request, success_message)
        else:
            self.message_user_warning(request)

        if "_continue" in request.POST:
            return HttpResponseRedirect(request.get_full_path())
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.get_attributes_model_list()

        if any(
                self.has_o2o(self.get_model(model_name))
                for model_name in self.models_list
        ):
            raise Http404

        # if any(
        #         (
        #                 isinstance(field, models.OneToOneField)
        #                 and not field.primary_key
        #         )
        #         for model_name in self.models_list
        #         for field in self.get_model(model_name)._meta.get_fields()
        # ):
        #     raise Http404

        # for model_name in self.models_list:
        #     model = self.get_model(model_name)
        #     fields = model._meta.get_fields()
        #     for field in fields:
        #         if (
        #                 isinstance(field, models.OneToOneField)
        #                 and not field.primary_key
        #         ):
        #             raise Http404

        self.user_perm = self.get_model_list_perms(request, self.models_list)

        if not self.user_perm.get('view'):
            raise Http404
        self.kwargs.update(action=self.action, current_app=self.app_label)

        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        if not self.user_perm.get('change'):
            self.get_attributes_model_list()
            self.user_perm = self.get_model_list_perms(
                request, self.models_list
            )
        if not self.user_perm.get('change'):
            raise Http404
        self.kwargs.update(action=self.action, current_app=self.app_label)

        formsets = []
        for model_index, model_name in enumerate(self.models_list):
            self.get_attributes_list(model_name)
            object_list = self.get_queryset()
            prefix = f'table-{model_index}-form'
            default = {'queryset': object_list, 'prefix': prefix}
            formset = self.get_formset(**default)
            formsets.append(formset)

        is_valid = kwargs['is_valid'] if kwargs.get('is_valid') else True
        for formset in formsets:
            if formset.is_valid() and is_valid:
                continue
            else:
                kwargs.update(formsets=formsets)
                return self.render_to_response(
                    self.get_context_data(**kwargs)
                )

        return self.formsets_valid(request, formsets, *args, **kwargs)


class MultipleListView(MultipleListMixin, TemplateView):
    """Несколько списков на одной странице."""


class ChangeFormView(DataFormMixin, FormView):
    """Изменения форм"""

    action = 'change'


class AddFormView(DataFormMixin, FormView):
    """Добавления форм"""

    action = 'add'

    def get_fieldsets(self, form):
        try:
            return form.Meta.add_fieldsets
        except AttributeError:
            return [(None, {"fields": self.get_fields(form)})]

    def get_fields(self, form=None):
        try:
            return form.Meta.add_fields
        except AttributeError:
            return super().get_fields(form)

    def get_readonly_fields(self, form=None):
        if form and hasattr(form, 'Meta'):
            if (
                    hasattr(form.Meta, 'add_fieldsets')
                    or hasattr(form.Meta, 'add_fields')
                    or hasattr(form.Meta, 'add_readonly_fields')
            ):
                return getattr(form.Meta, 'add_readonly_fields', ())
            else:
                return getattr(form.Meta, 'readonly_fields', ())
        else:
            return ()


class DeleteFormView(DataObjectMixin, TemplateView):
    """Удаление форм"""

    template_name = 'core/delete.html'
    action = 'delete'

    def get_deleted_objects(self, objs):
        using = router.db_for_write(objs[0]._meta.model)
        collector = NestedObjectsContract(using=using)
        # collector = NestedObjectsContract(using=using, origin=objs)
        collector.collect(objs)

        def format_callback(obj):
            opts = obj._meta
            try:
                url = obj.get_absolute_url()
            except NoReverseMatch:
                return "%s: %s" % (capfirst(opts.verbose_name), obj)

            return format_html(
                '{}: <a href="{}">{}</a>',
                capfirst(opts.verbose_name),
                url,
                obj
            )

        deleted_objects = collector.nested(format_callback)

        protected = [format_callback(obj) for obj in collector.protected]
        model_count = {
            model._meta.verbose_name_plural: len(objs)
            for model, objs in collector.model_objs.items()
        }
        return deleted_objects, model_count, protected

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        (deleted_objects,
         model_count,
         protected) = self.get_deleted_objects([self.object])
        context['deleted_objects'] = deleted_objects
        context['model_count'] = model_count.items()
        context['protected'] = protected
        context['object_name'] = self.model._meta.verbose_name
        try:
            context['object_url'] = format_html(
                '<a href="{}" class ="text">{}</a>',
                self.object.get_absolute_url(),
                self.object
            )
        except NoReverseMatch:
            context['object_url'] = self.object

        return context

    def get(self, request, *args, **kwargs):
        self.get_attributes_model()
        if not has_permission_delete(request, self.model):
            raise Http404
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.get_attributes_model()
        self.object = self.get_object()

        # Проверка наличия файлов, если есть удалить
        for field in self.object._meta.fields:
            if isinstance(field, (models.FileField, models.ImageField)):
                file = getattr(self.object, field.name)
                if file:
                    os.remove(file.path)

        # Формирование записи в журнал
        self.log_entry(request, self.object)
        # Формирование сообщения об успешном удалении объекта
        success_message = self.get_success_message(self.object)
        self.message_user_success(request, success_message)
        # self.object.delete() ###### включить
        return HttpResponseRedirect(self.get_success_url())


class HistoryListView(BaseSiteMixin, TemplateView):
    """История изменений объекта"""
    from risi.models import LogEntrySite

    model_history = LogEntrySite
    template_name = 'core/object_history.html'
    paginator_class = Paginator
    page_size = 50
    page_kwarg = "page"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        self.get_attributes_model()
        action_list = (
            self.model_history.objects.filter(
                object_id=self.obj_id,
                content_type=self.get_content_type_for_model(self.model),
            )
            .select_related()
            .order_by("action_time")
        )

        page_size = self.page_size
        page_var = self.page_kwarg
        paginator = self.paginator_class(action_list, page_size)
        page_number = self.request.GET.get(page_var, 1)
        page_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(page_obj.number)

        context = {
            "title": 'История изменений',
            "action_list": page_obj,
            "page_range": page_range,
            "page_var": page_var,
            "pagination_required": paginator.count > page_size,
        }
        context.update(kwargs)

        return context

    def get(self, request, *args, **kwargs):
        if not has_permission_view(request, self.model_history):
            raise Http404
        self.kwargs.update(action=self.action, current_app=self.app_label)

        return super().get(request, *args, **kwargs)
