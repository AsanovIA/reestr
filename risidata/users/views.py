from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
)
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import FormView
from django.utils.html import escape

from core.mixins import DataObjectMixin
from core.utils import has_permission_change, try_get_url, get_slug_url
from database.views import (
    ObjectListView as DatabaseObjectListView,
    ObjectAddView as DatabaseObjectAddView,
)
from users.forms import UserProfileCreationForm

APP_LABEL = 'users'

settings_dict = {
    'usergroup': {
        # 'fields_related': (),
        'fields_display': ('name',),
        'fields_link': ('name',),
        # 'fields_editable': ('view',),
        # 'readonly_fields': (),
    },
    'userprofile': {
        # 'fields_related': ('',),
        'fields_display': ('username', 'email', 'last_name', 'first_name',
                           'middle_name', 'is_active',),
        'fields_link': ('username',),
        'fields_editable': (),
        # 'readonly_fields': (),
    },
}


class ObjectListView(DatabaseObjectListView):
    """Список записей в модели"""

    def get_queryset(self, query=Q(), model=None):
        if self.model_name == 'userprofile':
            query = Q(('is_superuser', False), )
        return super().get_queryset(query)


class ObjectAddView(DatabaseObjectAddView):

    def get_form(self, form_class=None, **kwargs):
        if self.model_name == 'userprofile':
            self.form_class = UserProfileCreationForm
        return super().get_form(self.form_class)


class UserPasswordSetView(DataObjectMixin, FormView):
    """Установка пароля выбранной учетной записи"""

    app_label = APP_LABEL
    action = 'change'
    template_name = "users/password_set.html"
    form_class = AdminPasswordChangeForm

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.object
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context['title'] = 'Изменить пароль: %s' % escape(user.get_username())
        context.update(btn={
            'btn_change': True,
            'btn_text': 'Изменить пароль',
        })
        context['opts'] = self.model._meta
        context['username'] = user
        return context

    def form_valid(self, form):
        obj = form.save()

        # Запись в журнал
        self.log_change(obj, form)

        # Формирование сообщения об успешной записи
        success_message = format_html(
            f'Пароль для пользователя {str(obj)} успешно изменен.'
        )
        self.message_user_success(self.request, success_message)
        update_session_auth_hash(self.request, form.user)
        return HttpResponseRedirect(
            try_get_url(
                f'{APP_LABEL}_change',
                slug=get_slug_url(self.kwargs, obj_id=obj.pk),
                current_app=APP_LABEL
            )
        )

    def post(self, request, *args, **kwargs):
        self.get_attributes_model()
        if not has_permission_change(request, self.model):
            raise Http404
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
