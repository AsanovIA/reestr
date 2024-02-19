from copy import copy

from django.apps import apps
from django.contrib.admin.utils import (
    NestedObjects,
    label_for_field as label_for_field_admin
)
from django.contrib.auth import get_permission_codename
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db import models
from django.urls import reverse, NoReverseMatch

BLANK_CHOICE = [('', '---------')]
DEFAULT_MESSAGE_WARNING = 'Изменения отсутствуют. Сохранение отменено.'

DELETE_MODEL_OBJECT = [
    'Contract',
    'Letter',
    'AddAgreement',
    'Member',
]
SETTINGS_APP_LIST = [
    'users',
    'database',
]
TRANSTABLE = (
    ("'", "'"),
    ('"', '"'),
    ("‘", "'"),
    ("’", "'"),
    ("«", '"'),
    ("»", '"'),
    ("“", '"'),
    ("”", '"'),
    ("–", "-"),  # en dash
    ("—", "-"),  # em dash
    ("‒", "-"),  # figure dash
    ("−", "-"),  # minus
    ("…", "..."),
    ("№", "#"),
    # upper
    ("А", "A"),
    ("Б", "B"),
    ("В", "V"),
    ("Г", "G"),
    ("Д", "D"),
    ("Е", "E"),
    ("Ё", "E"),
    ("Ж", "ZH"),
    ("З", "Z"),
    ("И", "I"),
    ("Й", "I"),
    ("К", "K"),
    ("Л", "L"),
    ("М", "M"),
    ("Н", "N"),
    ("О", "O"),
    ("П", "P"),
    ("Р", "R"),
    ("С", "S"),
    ("Т", "T"),
    ("У", "U"),
    ("Ф", "F"),
    ("Х", "KH"),
    ("Ц", "TS"),
    ("Ч", "CH"),
    ("Ш", "SH"),
    ("Щ", "SHCH"),
    ("Ъ", "IE"),
    ("Ы", "Y"),
    ("Ь", ""),
    ("Э", "E"),
    ("Ю", "IU"),
    ("Я", "IA"),
    # lower
    ("а", "a"),
    ("б", "b"),
    ("в", "v"),
    ("г", "g"),
    ("д", "d"),
    ("е", "e"),
    ("ё", "e"),
    ("ж", "zh"),
    ("з", "z"),
    ("и", "i"),
    ("й", "i"),
    ("к", "k"),
    ("л", "l"),
    ("м", "m"),
    ("н", "n"),
    ("о", "o"),
    ("п", "p"),
    ("р", "r"),
    ("с", "s"),
    ("т", "t"),
    ("у", "u"),
    ("ф", "f"),
    ("х", "kh"),
    ("ц", "ts"),
    ("ч", "ch"),
    ("ш", "sh"),
    ("щ", "shch"),
    ("ъ", "ie"),
    ("ы", "y"),
    ("ь", ""),
    ("э", "e"),
    ("ю", "iu"),
    ("я", "ia"),
)  # https://github.com/last-partizan/pytils/blob/master/pytils/translit.py


class ChangeList:
    def __init__(
            self,
            request,
            object_list,
            model_view,
            model,
            form=None,
            fields_display=None,
            fields_link=None,
            fields_editable=None,

    ):
        self.formset = None
        self.model_view = copy(model_view)
        self.model, self.form = model, form
        self.opts = model._meta
        self.request = request
        self.root_queryset = object_list
        self.fields_display = fields_display
        self.fields_link = fields_link
        self.fields_editable = fields_editable
        self.pk_attname = self.opts.pk.attname

        self.queryset = self.get_queryset(request)
        result_list = self.queryset._clone()
        self.result_list = result_list
        self.result_count = len(result_list)

    def get_queryset(self, request):
        qs = self.root_queryset
        return qs

    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        app_label = self.model_view.app_label
        urlargs = {
            **self.model_view.kwargs,
            'slug': get_slug_url(
                self.model_view.kwargs, self.opts.model_name, pk
            )
        }
        return try_get_url(f'{app_label}_change', **urlargs)


def try_get_url(name, slug=None, current_app=None, **kwargs):
    if kwargs.get('action') == 'view':
        name = 'archive_' + name
    urlargs = {'slug': slug} if slug else None
    try:
        return reverse(name, kwargs=urlargs, current_app=current_app)
    except NoReverseMatch:
        return ''


def get_slug_kwarg(kwargs):
    slug = kwargs.get('slug')
    model_name = obj_id = related_id = None
    if slug:
        model_name, obj_id, related_id = slug.split('-')

    return [model_name, obj_id, related_id]


def get_slug_url(kwargs, model=None, obj_id=None, related_id=None):
    attr = get_slug_kwarg(kwargs)
    if model is not None:
        attr[0] = model if isinstance(model, str) else model._meta.model_name
    if obj_id is not None:
        attr[1] = str(obj_id)
    if related_id is not None:
        attr[2] = str(related_id)

    if attr[0] is None:
        raise ImproperlyConfigured('The model must be defined.')

    attr = ['0' if v is None else v for v in attr]
    slug = '-'.join(attr)

    return slug


def id_list(related_model, *model_list, **kwargs):
    """Возвращает список id связанной модели"""
    s = set()
    for model in model_list:
        query = models.Q((model._meta.model_name + '__isnull', False),)
        if kwargs:
            query &= models.Q(*kwargs.items())
        related_ids = related_model.objects.filter(query).values_list(
            'id', flat=True
        ).distinct()
        s.update(s, related_ids)
    return s


def label_for_column(name, model, form=None):
    try:
        field = form.declared_fields.get(name)
        label = field.label
    except AttributeError:
        field = model._meta.get_field(name)
        try:
            label = field.verbose_name
        except AttributeError:
            label = field.related_model._meta.verbose_name_plural

    return label


def label_for_field(
        name, model, model_view=None, return_attr=False, form=None
):
    attr = None
    try:
        field = form.declared_fields.get(name)
        label = field.label
    except AttributeError:
        if return_attr:
            label, attr = label_for_field_admin(
                name, model, model_view, return_attr, form)
        else:
            label = label_for_field_admin(
                name, model, model_view, return_attr, form)
    if return_attr:
        return (label, attr)
    else:
        return label


def help_text_for_field(name, model, form):
    help_text = ""
    try:
        field = form.declared_fields.get(name)
        if not field.help_text:
            field = model._meta.get_field(name)
        help_text = field.help_text
    except (FieldDoesNotExist, AttributeError):
        pass

    return help_text


def has_permission_change(request, model):
    opts = model._meta
    codename = get_permission_codename('change', opts)
    return request.user.has_perm("%s.%s" % (opts.app_label, codename))


def has_permission_add(request, model):
    opts = model._meta
    codename = get_permission_codename('add', opts)
    return request.user.has_perm("%s.%s" % (opts.app_label, codename))


def has_permission_delete(request, model):
    opts = model._meta
    codename = get_permission_codename('delete', opts)
    return request.user.has_perm("%s.%s" % (opts.app_label, codename))


def has_permission_close(request, model):
    opts = model._meta
    codename = get_permission_codename('close', opts)
    return request.user.has_perm(
        "%s.%s" % (opts.app_label, codename)
    ) and has_permission_change(request, model)


def has_permission_view(request, model):
    opts = model._meta
    codename = get_permission_codename('view', opts)
    return request.user.has_perm(
        "%s.%s" % (opts.app_label, codename)
    ) or has_permission_change(request, model)


def get_model_perms(request, model):
    return {
        "add": has_permission_add(request, model),
        "change": has_permission_change(request, model),
        "delete": has_permission_delete(request, model),
        "view": has_permission_view(request, model),
        "close": has_permission_close(request, model),
    }


def translit(text):
    if isinstance(text, str):
        for symbol_in, symbol_out in TRANSTABLE:
            text = text.replace(symbol_in, symbol_out)
    return text


def get_delete_models():
    models = list(apps.get_app_config('database').models.values())
    models_contract = apps.get_app_config('contract').models.values()
    models += [model for model in models_contract if
               model.__name__ in DELETE_MODEL_OBJECT]
    return models


class NestedObjectsContract(NestedObjects):
    def collect(self, objs, source=None, source_attr=None, **kwargs):
        delete_models = get_delete_models()
        for obj in objs:
            if obj._meta.model in delete_models:
                if source_attr and not source_attr.endswith("+"):
                    related_name = source_attr % {
                        "class": source._meta.model_name,
                        "app_label": source._meta.app_label,
                    }
                    self.add_edge(getattr(obj, related_name), obj)
                else:
                    self.add_edge(None, obj)
                self.model_objs[obj._meta.model].add(obj)
        try:
            return super(NestedObjects, self).collect(
                objs, source_attr=source_attr, **kwargs
            )
        except models.ProtectedError as e:
            self.protected.update(e.protected_objects)
        except models.RestrictedError as e:
            self.protected.update(e.restricted_objects)
