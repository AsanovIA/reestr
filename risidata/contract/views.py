from itertools import chain

from django import forms
from django.db import models
from django.db.models import Q
from django.http import (
    HttpResponseRedirect, JsonResponse, FileResponse, Http404
)
from django.urls import NoReverseMatch
from django.utils.html import format_html
from django.views.generic.base import View, TemplateView

from account.models import UserSettings
from account.views import UserSettingsView
from contract.forms import (
    ContractForm, LetterForm, AddAgreementForm, StageBeginListForm,
    StageMiddleListForm, StageEndListForm, StageAddForm, SetTimeWorkForm,
)
from contract.models import Contract
from core.mixins import (
    BaseSiteMixin, MultipleListView, DataObjectMixin,
    AddFormView, ChangeFormView, DeleteFormView, HistoryListView,
)
from core.utils import (
    has_permission_add, has_permission_change, has_permission_view,
    get_slug_url, try_get_url, id_list,

)
from database.models import Post, SubDivision, Employee, Client
from users.models import UserProfile

APP_LABEL = 'contract'

settings_dict = {
    'contract': {
        'fields_related': (
            'condition',
            'status',
            # 'control_price',
            'otvetstvenny',
            'soprovojdenie',
            'client',
            'great_client',
        ),
        'fields_display': ContractForm.Meta.fields,
        'fields_link': ('number',),
        # 'fields_editable': ('date',),
        'readonly_fields': (),
    },
    'member': {
        'fields_related': ('employee',),
        'fields_display': (
            'employee', 'otvetstvenny', 'ispolnitel', 'soprovojdenie',
        ),
        'fields_link': ('employee',),
        # 'fields_editable': ('date',),
        'readonly_fields': (),
    },
    'letter': {
        'fields_related': ('ispolnitel', 'ispolnitel__employee'),
        'fields_display': LetterForm.Meta.fields,
        'fields_link': ('number',),
        'fields_editable': ('status', 'date'),
        'readonly_fields': ('content',),
    },
    'addagreement': {
        # 'fields_related': (),
        'fields_display': AddAgreementForm.Meta.fields,
        'fields_link': ('number',),
        # 'fields_editable': ('date',),
        'readonly_fields': (),
    },
    'contact': {
        # 'fields_related': (),
        'fields_display': ('name', 'comment', 'post', 'division', 'telephone',
                           'email'),
        'fields_link': ('name',),
        # 'fields_editable': (),
        # 'readonly_fields': (),
    },
    'stagebeginlist': {
        'fields_related': ('name', 'ispolnitel'),
        'fields_display': StageBeginListForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('date_end_plan',),
        'readonly_fields': (),
    },
    'stagemiddlelist': {
        'fields_related': ('name', 'ispolnitel'),
        'fields_display': StageMiddleListForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('date_end_plan',),
        'readonly_fields': (),
    },
    'stageendlist': {
        'fields_related': ('name', 'ispolnitel'),
        'fields_display': StageEndListForm.Meta.fields,
        'fields_link': ('name',),
        # 'fields_editable': ('date_end_plan',),
        'readonly_fields': (),
    },
    'employee': {
        'fields_related': ('post', 'division'),
        'fields_display': ('__str__', 'tabel', 'post', 'division'),
        'fields_link': ('__str__',),
        # 'readonly_fields': (),
    },
    'timework': {
        'fields_related': ('member', 'member__employee'),
        'fields_display': ('member', 'time'),
        'fields_link': ('member',),
        'readonly_fields': (),
    },
}


class ContractMixin:
    app_label = APP_LABEL
    dict_models_list = {
        'stage': {
            'name': 'этап',
            'name_plural': 'этапы',
            'suffix': 'ы',
            'list': ['stagebeginlist', 'stagemiddlelist', 'stageendlist'],
            'fields': ['stage_begin', 'stage_middle', 'stage_end'],
        },
    }

    @property
    def sidebar(self):
        if (
                self.model_name == 'contract'
                and self.obj_id == '0'
                and self.related_id == '0'
        ):
            # return 'filter_sidebar'
            return None
        return 'nav_sidebar'

    @property
    def media(self):
        js = []
        if self.model_name == 'contract' and self.sidebar == 'nav_sidebar':
            js += ['contract.js']

        return forms.Media(js=["contract/js/%s" % url for url in js])

    def get_query(self):
        if self.model_name == 'contract':
            return Q(closed=False)
        else:
            return Q(('contract__closed', False), )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.model_name != 'contract':
            kwargs['contract_id'] = self.get_contract_id()
        if self.get_model_name() == 'stage' and 'instance' in kwargs:
            del kwargs['instance']
        return kwargs

    def get_navigation_list(self, request, pk):
        """Боковая панель навигации"""

        action = self.action
        utlargs = {**self.kwargs}
        menu = []
        exclude_model = [
            value
            for k in self.dict_models_list
            for value in self.dict_models_list[k]['list']
        ] + ['timework']
        related_models = Contract._meta.related_objects
        for obj in chain(related_models, self.dict_models_list):
            if obj is None:
                continue
            if isinstance(obj, str):
                model_list = [
                    self.get_model(model_name)
                    for model_name in self.dict_models_list[obj]['list']
                ]
                model_name = obj
                vnp = self.dict_models_list[obj]['name_plural']
            else:
                model = obj.related_model
                opts = model._meta
                model_list = [model]
                if opts.model_name in exclude_model:
                    continue
                model_name = opts.model_name
                vnp = opts.verbose_name_plural
            if not all(
                    has_permission_view(request, model) for model in model_list
            ):
                continue

            model_dict = {
                'name': model_name,
                'vnp': vnp.capitalize(),
                'perms': {},
            }
            if (
                    all(has_permission_change(request, model)
                        for model in model_list)
                    and action != 'view'
            ):
                model_dict['perms']['change'] = True

            if isinstance(obj, models.OneToOneRel):
                utlargs.update(slug=get_slug_url({}, model_name, pk, pk))
                model_dict["list_url"] = try_get_url(
                    f'{APP_LABEL}_change', **utlargs
                )
            elif (
                    isinstance(obj, models.ManyToOneRel)
                    or isinstance(obj, str)
            ):
                utlargs.update(slug=get_slug_url({}, model_name, '0', pk))
                model_dict["list_url"] = try_get_url(
                    f'{APP_LABEL}_list', **utlargs
                )
                if (
                        all(has_permission_add(request, model)
                            for model in model_list)
                        and action != 'view'
                ):
                    model_dict['perms']['add'] = True
                    model_dict["add_url"] = try_get_url(
                        f'{APP_LABEL}_add', **utlargs
                    )

            menu.append(model_dict)
        menu.sort(key=lambda x: x["vnp"].lower())
        return menu

    def get_num_contract(self, pk):
        from core.models import NUMBER_EMPTY

        num_contract = Contract.objects.values('number').get(pk=pk)['number']
        return num_contract or NUMBER_EMPTY

    def get_url_contract(self, pk):
        urlargs = {
            **self.kwargs,
            'slug': get_slug_url({}, 'contract', pk)
        }
        return try_get_url(f'{self.app_label}_change', **urlargs)

    def get_contract_id(self):
        return self.obj_id if self.related_id == '0' else self.related_id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['sidebar'] == 'nav_sidebar':
            pk = self.get_contract_id()
            context['related_name'] = num_contract = self.get_num_contract(pk)
            context['related_url'] = related_url = self.get_url_contract(pk)
            context['model_list'] = self.get_navigation_list(self.request, pk)
            context['main_url_text'] = 'Список договоров'
            urlargs = {**self.kwargs, 'slug': get_slug_url({}, 'contract')}
            context['main_url'] = try_get_url('contract_list', **urlargs)

            if self.action == 'close':
                context['object_name'] = self.model._meta.verbose_name
                try:
                    context['object_url'] = format_html(
                        '<a href="{}" class ="text">{}</a>',
                        related_url,
                        num_contract
                    )
                except NoReverseMatch:
                    context['object_url'] = num_contract

        return context

    def action_pre_save(self, obj, form, *args, **kwargs):
        super().action_pre_save(obj, form)
        if self.action == 'add' and self.model_name != 'contract':
            obj.contract_id = self.related_id


class ObjectListView(ContractMixin, MultipleListView):
    """Список форм"""

    def get_filters(self):
        """Фильтры
            'title' - заголовок фильтра,
            'name' - название фильтра в GET запросе,
            'select' - переменная для записи выбранного значения,
            'queryitems' - список из базы данных,
        """
        filters = {
            'condition': {
                'title': 'состояние:',
                'name': 'condition',
                'select': '',
                'queryitems': ConditionContract.objects.all(),
            },
            'status': {
                'title': 'статус:',
                'name': 'status',
                'select': '',
                'queryitems': StatusContract.objects.all(),
            },
            # 'controlPrice': {
            #     'title': 'контроль цены:',
            #     'name': 'control_price',
            #     'select': '',
            #     'queryitems': ControlPrice.objects.all(),
            # },
            'otvetstvenny': {
                'title': 'Ответственный:',
                'name': 'otvetstvenny',
                'select': '',
                'queryitems': UserProfile.objects.filter(otvetstvenny=True),
            },
            'soprovojdenie': {
                'title': 'Сопровождение:',
                'name': 'soprovojdenie',
                'select': '',
                'queryitems': UserProfile.objects.filter(soprovojdenie=True),
            },
            'ispolnitel': {
                'title': 'Исполнитель:',
                'name': 'ispolnitel',
                'select': '',
                # 'queryitems': get_contract_id(UserProfile, kwargs={'user_otvetstvenny': True}),
                'queryitems': UserProfile.objects.filter(ispolnitel=True),
            },
            'middlename': {
                'title': 'этапы выполнения',
                'name': 'middlename',
                'select': '',
                # 'queryitems': get_contract_id(UserProfile, kwargs={'user_otvetstvenny': True}),
                'queryitems': StageMiddleName.objects.all(),
            },
        }
        return filters

    def get_changelist_instance(self, formset=None, **kwargs):
        if self.model_name != 'contract':
            return super().get_changelist_instance(formset, **kwargs)
        ChangeList = self.get_changelist()
        object_list = kwargs.get('queryset')
        cl = ChangeList(
            self.request, object_list, self, self.model, self.form_changelist
        )
        user_settings = UserSettings.objects.get(user=self.request.user)
        settings = user_settings.get_settings()
        cl.columns = settings.get('contract_list', ['number'])

        related_models = [
            model.related_model
            for model in Contract._meta.related_objects
            if model.one_to_many and model.name in cl.columns
        ]
        check = {}
        for model in related_models:
            ids = id_list(Contract, model)
            check.update({model._meta.model_name: ids})
        cl.check = check

        return cl

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if self.model_name == 'contract':
        #     context['filters'] = self.get_filters()

        return context

    def get_queryset(self, query=Q(), model=None):
        query &= self.get_query()
        if self.model_name != 'contract':
            query &= Q(('contract__id', self.related_id), )
        return super().get_queryset(query)


class ObjectChangeView(ContractMixin, ChangeFormView):
    """Изменения форм"""

    template_name = 'contract/change_form.html'

    def get_close_url(self, obj):
        slug = get_slug_url(self.kwargs, obj_id=obj.pk)
        return try_get_url(f'{self.app_label}_close', slug, self.app_label)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model_name == 'contract' and self.action == 'change':
            from core.utils import has_permission_close

            if has_permission_close(self.request, self.model):
                # пользователь имеет права изменения и закрытия договора
                context['close_url'] = self.get_close_url(self.object)
                context['close'] = True

        return context

    def get_queryset(self, query=Q()):
        query &= self.get_query()
        if self.has_o2o(self.model):
            query &= Q(('contract__id', self.related_id), )
        else:
            query &= Q(('pk', self.obj_id), )

        return super().get_queryset(query)


class ObjectAddView(ContractMixin, AddFormView):
    """Добавления форм"""

    def get_form(self, form_class=None, **kwargs):
        if self.get_model_name() == 'stage':
            self.form_class = StageAddForm
        return super().get_form(self.form_class)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (
                self.get_model_name() == 'stage'
                and 'btn' in context
                and 'btn_save_and_continue' in context['btn']
        ):
            del context['btn']['btn_save_and_continue']

        return context

    def form_valid(self, form):
        if self.get_model_name() not in self.dict_models_list:
            return super().form_valid(form)
        elif self.get_model_name() == 'stage':
            if form.has_changed():
                name_list = 'stage'
                suffix = self.dict_models_list[name_list]['suffix']
                name = self.dict_models_list[name_list]['name'].capitalize()
                fields_list = self.form_class.Meta.fields
                # fields_list = self.dict_models_list[name_list]['fields']
                model_list = [
                    self.get_model(model_name)
                    for model_name in self.dict_models_list[name_list]['list']
                ]
                changecount = 0
                for field, model in zip(fields_list, model_list):
                    values = form.cleaned_data.get(field)
                    if values:
                        for value in values:
                            model.objects.create(
                                contract_id=self.related_id, name=value,
                            )
                            changecount += 1

                # Формирование сообщения об успешной записи
                if changecount:
                    suffix = '' if changecount == 1 else suffix
                    success_message = (
                        f'{name}{suffix} успешно добавлен{suffix}.')
                    self.message_user_success(self.request, success_message)
            else:
                self.message_user_warning(self.request)

            return HttpResponseRedirect(self.get_success_url())


class ObjectDeleteView(ContractMixin, DeleteFormView):
    """Удаление форм"""


class ObjectHistoryView(ContractMixin, HistoryListView):
    """История изменений объекта"""


class ProjectsView(BaseSiteMixin, TemplateView):
    """Список проектов сайта - Главная страница"""

    template_name = 'core/index.html'

    def get_index_list(self):
        """Список проектов сайта"""

        project_list = []
        projects = [
            'contract',
            'employee'
        ]
        for project in projects:
            model = self.get_model(project)
            app_label = model._meta.app_label
            name = f'{project}_list'
            slug = get_slug_url({}, project)
            list_url = try_get_url(name, slug, current_app=app_label)
            app_dict = {
                "vnp": model._meta.verbose_name_plural,
                "label": app_label,
                "list_url": list_url,
            }

            project_list.append(app_dict)

        return project_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['caption'] = 'Проекты'
        context['index_list'] = self.get_index_list()
        return context


# class MainListView(MultipleListView):
# class MainListView(BaseSiteMixin, ListView):
#     """Главная страница (список договоров)"""
#
#     model = Contract
#     sidebar = 'filter_sidebar'
#     app_label = APP_LABEL
#     object_verbose_name = model._meta.verbose_name
#
#     def get_filters(self):
#         """Фильтры
#             'title' - заголовок фильтра,
#             'name' - название фильтра в GET запросе,
#             'select' - переменная для записи выбранного значения,
#             'queryitems' - список из базы данных,
#         """
#         filters = {
#             'condition': {
#                 'title': 'состояние:',
#                 'name': 'condition',
#                 'select': '',
#                 'queryitems': ConditionContract.objects.all(),
#             },
#             'status': {
#                 'title': 'статус:',
#                 'name': 'status',
#                 'select': '',
#                 'queryitems': StatusContract.objects.all(),
#             },
#             # 'controlPrice': {
#             #     'title': 'контроль цены:',
#             #     'name': 'control_price',
#             #     'select': '',
#             #     'queryitems': ControlPrice.objects.all(),
#             # },
#             'otvetstvenny': {
#                 'title': 'Ответственный:',
#                 'name': 'otvetstvenny',
#                 'select': '',
#                 'queryitems': UserProfile.objects.filter(otvetstvenny=True),
#             },
#             'soprovojdenie': {
#                 'title': 'Сопровождение:',
#                 'name': 'soprovojdenie',
#                 'select': '',
#                 'queryitems': UserProfile.objects.filter(soprovojdenie=True),
#             },
#             'ispolnitel': {
#                 'title': 'Исполнитель:',
#                 'name': 'ispolnitel',
#                 'select': '',
#                 # 'queryitems': get_contract_id(UserProfile, kwargs={'user_otvetstvenny': True}),
#                 'queryitems': UserProfile.objects.filter(ispolnitel=True),
#             },
#             'middlename': {
#                 'title': 'этапы выполнения',
#                 'name': 'middlename',
#                 'select': '',
#                 # 'queryitems': get_contract_id(UserProfile, kwargs={'user_otvetstvenny': True}),
#                 'queryitems': StageMiddleName.objects.all(),
#             },
#         }
#         return filters
#
#     def get_changelist_instance(self, formset=None, **kwargs):
#         from core.utils import ChangeList
#
#         # ChangeList = self.get_changelist()
#         cl = ChangeList(self.request, self.object_list, self, self.model)
#         user_settings = UserSettings.objects.get(user=self.request.user)
#         settings = user_settings.get_settings()
#         cl.columns = settings.get('contract_list', ['number'])
#
#         return cl
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # context['filters'] = self.get_filters()
#         # context['title'] = 'Список договоров'
#         # context['cl'] = context['cls'][0]
#         # del context['cls']
#         context['cl'] = self.get_changelist_instance()
#         if has_permission_add(self.request, Contract):
#             context['perm_add'] = True
#             context['btn']['btn_add'] = True
#             context['add_url'] = self.get_add_url()
#             context['verbose_name'] = self.model._meta.verbose_name
#         return context
#
#     def get_queryset(self, query=Q(), model=None):
#         query = Q(closed=False)
#         return self.model.objects.filter(query).select_related(
#             'condition',
#             'status',
#             # 'control_price',
#             'otvetstvenny',
#             'soprovojdenie',
#             'client',
#             'great_client',
#         )


class ContractCloseView(ContractMixin, DataObjectMixin, TemplateView):
    """Удаление договора"""

    template_name = 'core/close.html'
    action = 'close'

    def post(self, request, *args, **kwargs):
        self.get_attributes()
        obj = Contract.objects.get(pk=self.obj_id)
        obj.closed = True  ###### включить
        obj.save()

        # Формирование записи в журнал
        change_message = 'Договор закрыт'
        self.log_entry(self.request, obj, change_message)

        # Формирование сообщения об успешном закрытии
        obj_url = obj.get_absolute_url()
        success_message = format_html(
            'Договор {} успешно закрыт. Можете просмотреть его в архиве',
            format_html('<a href="{}">{}</a>', obj_url, str(obj)),
        )
        self.message_user_success(request, success_message)
        return HttpResponseRedirect(self.get_success_url())


class SettingsContractListView(UserSettingsView):
    """Настройка отображения списка договоров"""

    model = Contract
    name_settings = 'contract_list'
    count_columns = 9
    first_column = 'number'
    exclude_fields = [
        'id',
        'last_change',
        'closed',
        'stagebeginlist',
        'stagemiddlelist',
        'stageendlist',
        'timework',
    ]

    def get_content_title(self):
        return 'Содержимое столбцов таблицы списка договоров'


class EmployeeListView(MultipleListView):
    """Список сотрудников"""
    sidebar = None
    model = Employee
    app_label = APP_LABEL
    btn_add = False

    def get_changelist(self):
        from core.utils import ChangeList

        class EmployeeChangeList(ChangeList):
            def url_for_result(self, result):
                pk = getattr(result, self.pk_attname)
                model_name = 'timework'
                slug = get_slug_url({}, model_name, obj_id=pk)
                return try_get_url('employee_change', slug, APP_LABEL)

        return EmployeeChangeList

    def get_queryset(self, query=Q(), model=None):
        query &= Q(view=True)
        return super().get_queryset(query)

    def get(self, request, *args, **kwargs):
        self.app_label = self.model._meta.app_label
        return super().get(request, *args, **kwargs)


class EmployeeChangeView(MultipleListView):
    """"""
    template_name = 'contract/time_work_change_list.html'
    app_label = APP_LABEL
    btn_add = False
    form_class = SetTimeWorkForm

    opts_dict = {
        'timework': {
            'fields_related': ('contract',),
            'fields_display': ('contract', 'time'),
            'fields_link': ('contract',),
            'fields_editable': ('time',),
            'readonly_fields': (),
        },
    }

    def get_success_url(self):
        slug = get_slug_url({}, 'employee')
        return try_get_url('employee_list', slug, 'contract')

    def get_date(self):
        import datetime

        date_string = self.request.GET.get('date')
        if date_string:
            try:
                # для Django4
                return datetime.datetime.strptime(
                    date_string, "%d.%m.%Y"
                ).date()
            except ValueError:
                # для Django3
                return datetime.datetime.strptime(
                    date_string, "%Y-%m-%d"
                ).date()
        return datetime.date.today()

    def get_initial(self):
        return {'date': self.get_date()}

    def get_changelist(self):
        from core.utils import ChangeList

        class TimeWorkChangeList(ChangeList):
            def url_for_result(self, result):
                pk = getattr(result, self.pk_attname)
                model_name = 'contract'
                slug = get_slug_url({}, model_name, obj_id=pk)
                app_label = self.model_view.app_label
                return try_get_url(f'{app_label}_change', slug, app_label)

        return TimeWorkChangeList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Время сотрудника'
        if "form_object" not in context:
            self.object = Employee.objects.get(pk=self.obj_id)
        context['total_result_count'] += len(self.get_formset_initial())
        if context['total_result_count']:
            form = context.get('form_object') or self.get_form()
            site_form = self.get_site_form(form)
            context['siteform'] = site_form
            context['media'] += site_form.media
            context['btn']['btn_save_and_continue'] = True
        else:
            context['content_title'] = format_html(
                '{} не задействован ни в одном проекте.',
                str(self.object)
            )
        return context

    def get_queryset(self, query=Q(), model=None):
        query = Q(
            member_id=self.obj_id,
            date=self.get_date()
        )
        queryset = super().get_queryset(query)

        # Формирование списка проектов и помещение его в initial
        initial_query = Q(
            member__employee_id=self.obj_id,
            closed=False
        ) & ~Q(
            timework__date=self.get_date(),
            timework__member_id=self.obj_id
        )
        contracts = super().get_queryset(initial_query, Contract)
        self.formset_initial = [
            {'contract': contract} for contract in contracts
        ]

        return queryset

    def action_pre_save(self, obj, form, *args, **kwargs):
        super().action_pre_save(obj, form, *args, **kwargs)
        form_object = kwargs['form_object']
        if obj.id is None:
            obj.contract = form.initial['contract']
            obj.member_id = form_object.instance.id
            obj.date = form_object.cleaned_data.get('date')

    def log_change(self, obj, form, add=False):
        """Отключение записи изменений в журнал"""
        pass

    def post(self, request, *args, **kwargs):
        self.get_attributes_model_list()
        self.user_perm = self.get_model_list_perms(request, self.models_list)

        if not self.user_perm.get('change'):
            raise Http404

        self.object = Employee.objects.get(pk=self.obj_id)
        form = self.get_form()
        kwargs.update(form_object=form, is_valid=form.is_valid())

        return super().post(request, *args, **kwargs)


class ArchiveMixin:
    """Архив"""
    action = 'view'
    btn_add = False
    btn_save = False

    def get_query(self):
        if self.model_name == 'contract':
            return Q(closed=True)
        else:
            return Q(('contract__closed', True), )


class ArchiveListView(ArchiveMixin, ObjectListView):
    """Архив - списки форм"""


class ArchiveChangeView(ArchiveMixin, ObjectChangeView):
    """Архив - формы"""


class ArchiveHistoryView(ArchiveMixin, ObjectHistoryView):
    """Архив - история изменений"""


class ValueChangeView(View):
    """Автозаполнение объектов при выборе значений в списке"""

    def get(self, request):
        new_data = {'element': request.GET.get('element')}
        if new_data['element'] == 'client_name':
            if request.GET.get('id'):
                data = Client.objects.filter(pk=request.GET.get('id')).values(
                    'city', 'inn', 'department__name').first()
            else:
                data = {'city': '', 'inn': '', 'department__name': ''}
        elif new_data['element'] == 'post_abbr':
            if request.GET.get('id'):
                data = Post.objects.filter(pk=request.GET.get('id')).values(
                    'abbr').first()
            else:
                data = {'abbr': ''}
        elif new_data['element'] == 'division':
            if request.GET.get('id'):
                second_list = SubDivision.objects.filter(
                    division__id=request.GET.get('id'))
                data = [{'id': item.id, 'text': item.name} for item in
                        second_list]
            else:
                second_list = SubDivision.objects.all()
                data = [{'id': item.id, 'text': item.name} for item in
                        second_list]

        new_data.update(data=data)

        return JsonResponse(new_data, safe=False)

# class FilterContractView(MainListView):
#     """Работа фильтров по договорам боковой панели"""
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['filters']['condition']['select'] = self.request.GET.get('condition')
#         context['filters']['status']['select'] = self.request.GET.get('status')
#         context['filters']['controlPrice']['select'] = self.request.GET.get('control_price')
#         context['filters']['otvetstvenny']['select'] = self.request.GET.get('otvetstvenny')
#         context['filters']['soprovojdenie']['select'] = self.request.GET.get('soprovojdenie')
#         context['filters']['ispolnitel']['select'] = self.request.GET.get('ispolnitel')
#         context['filters']['middlename']['select'] = self.request.GET.get('middlename')
#         context['date'] = self.request.GET.get('date')
#         return context
#
#     def get_query(self):
#         query = self.query
#         kwargs = {}
#         for key, value in self.request.GET.items():
#             if hasattr(self.model, key + '_id'):
#                 if value:
#                     kwargs[key + '__name'] = value
#             # elif hasattr(self.model, key):
#             #     print(key, 'поле')
#             else:
#                 print(key, 'связь')
#
#         query &= Q(*kwargs.items())
#
#         # item = self.request.GET.getlist("condition")[0]
#         # if item:
#         #     query &= Q(condition__in=item)
#         #
#         # item = self.request.GET.getlist("status")[0]
#         # if item:
#         #     query &= Q(status__in=item)
#         #
#         # item = self.request.GET.getlist("control_price")[0]
#         # if item:
#         #     query &= Q(control_price__in=item)
#         #
#         # item = self.request.GET.getlist("otvetstvenny")[0]
#         # if item:
#         #     query &= Q(otvetstvenny__in=item)
#         #
#         # item = self.request.GET.getlist("soprovojdenie")[0]
#         # if item:
#         #     query &= Q(soprovojdenie__in=item)
#
#         item = self.request.GET.getlist("ispolnitel")[0]
#         if item:
#             kwargs = {'ispolnitel__name': item}
#             # name = UserProfile.objects.get(name=item)
#             # kwargs = {'ispolnitel': name}
#             query_kwargs = get_contract_id(*STAGE_MODEL_LIST, **kwargs)
#             query &= Q(id__in=query_kwargs)
#
#         item = self.request.GET.getlist("middlename")[0]
#         if item:
#             kwargs = {'name': item}
#             date_s = self.request.GET.getlist("date")[0]
#             if date_s:
#                 kwargs.update(date_end_prognoz__lte=date_s)
#             # name = StageMiddleName.objects.get(pk=item).name
#             # kwargs = {'name': name}
#             query_kwargs = get_contract_id(*STAGE_MODEL_LIST, **kwargs)
#             # query_kwargs = get_contract_id(StageBeginList, StageMiddleList, StageEndList, **kwargs)
#             query &= Q(id__in=query_kwargs)
#
#         return query
