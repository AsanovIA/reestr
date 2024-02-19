from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    ReadOnlyPasswordHashField,
    #################### не работает в django 3 ####################
    # , BaseUserCreationForm,
)
from django.contrib.auth.models import Permission
from django.db.models import Q

from core.forms import (
    HELP_MAX_SYMBOL,
    MAX_LENGTH,
    HELP_AUTOFILL,
    HELP_FILTER_HORIZONTAL,
)
from core.validators import cyrillic_validator
from core.widgets import FilteredSelectMultiple
from users.models import UserGroup, UserProfile

EXCLUDE_PERMISSIONS = (
        ~(Q(content_type__app_label='admin') |
          Q(content_type__app_label='auth') |
          Q(content_type__app_label='sessions') |
          Q(content_type__app_label='contenttypes') |
          Q(content_type__app_label='risi') |
          Q(content_type__app_label='account') |
          Q(codename='add_calculation') |
          Q(codename='delete_calculation')
          ) |
        (
            Q(codename='view_logentrysite')
        )
)


class UserGroupForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100, help_text=HELP_MAX_SYMBOL % 100, label='Название'
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(EXCLUDE_PERMISSIONS).select_related(
            'content_type'
        ),
        widget=FilteredSelectMultiple(verbose_name='Права', is_stacked=False),
        required=False,
        help_text=HELP_FILTER_HORIZONTAL,
        label='Права'
    )

    class Meta:
        model = UserGroup
        fields = ['name', 'permissions']


class UserProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=MAX_LENGTH, label='Логин')
    email = forms.EmailField(
        max_length=MAX_LENGTH,
        label='Адрес электронной почты',
    )
    last_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Фамилия',
    )
    first_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Имя',
    )
    middle_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Отчество',
    )
    password = ReadOnlyPasswordHashField(
        label='Пароль',
        help_text='Пароли хранятся в зашифрованном виде, поэтому нет '
                  'возможности посмотреть пароль этого пользователя, но вы '
                  'можете изменить его используя '
                  '<a href="{}">эту форму</a>.'
    )
    is_active = forms.BooleanField(
        initial=True,
        required=False,
        label='Активный',
        help_text='Отметьте, если пользователь должен считаться активным. '
                  'Уберите эту отметку вместо удаления учётной записи.'
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=UserGroup.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name='Группа', is_stacked=False),
        label='Группы',
        help_text='Пользователь получит все права, указанные в каждой из '
                  'групп. ' + HELP_FILTER_HORIZONTAL
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(EXCLUDE_PERMISSIONS).select_related(
            'content_type'
        ),
        required=False,
        widget=FilteredSelectMultiple(verbose_name='Права', is_stacked=False),
        label='Права пользователя',
        help_text='Индивидуальные права данного пользователя. '
                  + HELP_FILTER_HORIZONTAL
    )

    class Meta:
        model = UserProfile
        fieldsets = (
            (None, {'fields': ('password',)}),
            (
                'Персональная информация',
                {'fields': (
                    'last_name',
                    'first_name',
                    'middle_name',
                    'username',
                    'email',
                )}
            ),
            (
                'Права доступа',
                {'fields': ('is_active', 'groups', 'user_permissions')}
            ),
        )
        fields = [
            'username', 'password', 'email', 'last_name', 'first_name',
            'middle_name', 'is_active', 'groups', 'user_permissions',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password:
            password.help_text = password.help_text.format(
                f"../../userprofile-{self.instance.pk}-0/password/"
            )
        user_permissions = self.fields.get("user_permissions")
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related(
                "content_type"
            )


class UserProfileCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=MAX_LENGTH,
        required=False,
        label='Логин',
        help_text=HELP_AUTOFILL,
    )
    email = forms.EmailField(
        max_length=MAX_LENGTH,
        required=False,
        label='Адрес электронной почты',
        help_text=HELP_AUTOFILL,
    )
    last_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Фамилия',
    )
    first_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Имя',
    )
    middle_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Отчество',
    )

    class Meta:
        model = UserProfile
        fields = (
            'last_name', 'first_name', 'middle_name',
            'username', 'email', 'password1', 'password2',
        )
        readonly_fields = ('username', 'email')

    #################### не работает в django 3 ####################
    # def __init__(self, *args, **kwargs):
    #     super(BaseUserCreationForm, self).__init__(*args, **kwargs)
    #     self.fields[self.Meta.fields[0]].widget.attrs[
    #         "autofocus"
    #     ] = True

    @property
    def media(self):
        return forms.Media(js=["contract/js/userprofile.js"])


class AdminUserProfileCreationForm(UserCreationForm):
    last_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Фамилия',
    )
    first_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Имя',
    )
    middle_name = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator],
        label='Отчество',
    )

    class Meta:
        model = UserProfile
        fields = (
            'last_name', 'first_name', 'middle_name',
            'username', 'email', 'password1', 'password2',
        )
        # readonly_fields = ('username', 'email')
        # field_classes = {"username": UsernameField}
        # widgets = {
        #     'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        #     'email': forms.TextInput(attrs={'readonly': 'readonly'}),
        # }

    #################### не работает в django 3 ####################
    # def __init__(self, *args, **kwargs):
    #     super(BaseUserCreationForm, self).__init__(*args, **kwargs)
    #     self.fields[self.Meta.fields[0]].widget.attrs[
    #         "autofocus"
    #     ] = True

    @property
    def media(self):
        return forms.Media(js=["contract/js/userprofile.js"])
