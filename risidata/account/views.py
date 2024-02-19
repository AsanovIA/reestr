from django.apps import apps
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.views.generic import FormView, TemplateView

from account.forms import UserSettingsForm
from account.models import UserSettings
from core.mixins import BaseSiteMixin
from core.utils import has_permission_view, try_get_url

APP_LABEL = 'account'


class AccountMixin:

    sidebar = 'menu_sidebar'

    def get_index_list(self):
        return [
            {
                'name': '',
                'vnp': 'изменить пароль',
                'url': try_get_url('password_change', current_app=APP_LABEL)
            },
            {
                'name': '',
                'vnp': 'содержимое списка проектов',
                'url': try_get_url(
                    'contract_list_change', current_app='contract'
                )
            },
        ]

    def construct_index_list(self):
        """Боковая панель навигации"""

        app_list = []
        model_list = []
        for obj in self.get_index_list():
            model_dict = {
                'name': obj['name'],
                'vnp': obj['vnp'],
                'perms': {'change': True},
                'list_url': obj['url'],
            }

            model_list.append(model_dict)
        # menu.sort(key=lambda x: x["vnp"].lower())

        app_dict = {
            "name": apps.get_app_config(APP_LABEL).verbose_name,
            "app_label": APP_LABEL,
            "app_url": try_get_url(
                'account_settings', current_app=APP_LABEL
            ),
            "models": model_list,
        }
        app_list.append(app_dict)

        return app_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caption'] = 'Аккаунт'
        context['app_list'] = self.construct_index_list()
        return context


class AccountSettingsView(AccountMixin, BaseSiteMixin, TemplateView):
    """Настройки аккаунта"""

    template_name = 'database/index.html'
    sidebar = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Аккаунт'
        return context


class UserPasswordChangeView(AccountMixin, BaseSiteMixin, PasswordChangeView):
    """Изменение пароля своей учетной записи"""

    template_name = "account/password_change.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy('account_settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn']['btn_change'] = True
        context['btn']['btn_text'] = 'Изменить мой пароль'
        return context

    def form_valid(self, form):
        success_message = format_html('Ваш пароль был успешно изменен.')
        self.message_user_success(self.request, success_message)
        return super().form_valid(form)


class UserSettingsView(AccountMixin, BaseSiteMixin, FormView):
    """Настройки. Изменение последовательности и содержимое отображения."""

    count_columns = 1
    exclude_fields = []
    template_name = "account/user_settings.html"
    first_column = None
    form_class = UserSettingsForm
    model = None
    name_settings = ''
    success_url = reverse_lazy('account_settings')

    def get_choices(self):
        from core.utils import BLANK_CHOICE

        form_class_model = self.get_form_class_model()()
        opts = self.model._meta
        try:
            choices = [
                (k, v.label.capitalize())
                for k, v in form_class_model.fields.items()
            ]
        except AttributeError:
            choices = [
                (field.name, field.verbose_name.capitalize())
                for field in opts.fields
                if field.name not in self.exclude_fields
            ]
        related_models = opts.related_objects
        choices += [
            (
                field.name,
                field.related_model._meta.verbose_name_plural.capitalize()
            )
            for field in related_models
            if (
                    field.name not in self.exclude_fields
                    and has_permission_view(self.request, field.related_model)

            )
        ]
        choices.sort(key=lambda x: x[1])
        choices = BLANK_CHOICE + choices
        return choices

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.model is None:
            raise ImproperlyConfigured(
                "Using UserSettingsView (base class of %(cls)s) without "
                "the 'model' attribute is prohibited. Define %(cls)s.model."
                % {"cls": self.__class__.__name__}
            )
        kwargs["count_columns"] = self.count_columns
        kwargs["first_column"] = self.first_column
        kwargs["choices"] = self.get_choices()
        self.user_settings = UserSettings.objects.get(user=self.request.user)
        settings = self.user_settings.get_settings()
        kwargs["settings"] = settings.get(self.name_settings)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_settings'] = self.name_settings
        context['content_title'] = self.get_content_title
        context['btn']['btn_save'] = True
        context['btn']['btn_save_and_continue'] = True
        return context

    def get_content_title(self):
        return ('Содержимое и последовательность отображения для %s.'
                % self.model._meta.verbose_name_plural)

    def form_valid(self, form):
        if form.has_changed():
            self.user_settings.update_settings(
                self.name_settings, form.cleaned_data
            )
            success_message = format_html('Настройки успешно изменены.')
            self.message_user_success(self.request, success_message)
        else:
            self.message_user_warning(self.request)

        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = "account/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    auth_logout(request)
    return redirect('login')
