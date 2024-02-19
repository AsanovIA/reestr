from django import forms
from core.forms import ViewField, HELP_MAX_SYMBOL, MAX_LENGTH
from core.validators import cyrillic_validator

from .models import *


class PostForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Должность')
    abbr = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Должность сокращенно')

    class Meta:
        model = Post
        fields = ['name', 'abbr', 'view']


class DivisionForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Подразделение')

    class Meta:
        model = Division
        fields = ['name', 'view']


class SubDivisionForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Субподразделение')
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(), label='Подразделение'
    )

    class Meta:
        model = SubDivision
        fields = ['division', 'name', 'view']


class ConditionContractForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Состояние договора')

    class Meta:
        model = ConditionContract
        fields = ['name', 'view']


class StatusContractForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Статус договора')

    class Meta:
        model = StatusContract
        fields = ['name', 'view']


# class ControlPriceForm(ViewField):
#     name = forms.CharField(max_length=MAX_LENGTH,
#                            help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
#                            label='Контроль ВП на ценообразование')
#
#     class Meta:
#         model = ControlPrice
#         fields = ['name', 'view']


class DepartmentForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Ведомство')

    class Meta:
        model = Department
        fields = ['name', 'view']


class ClientForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Организация')
    city = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        required=False,
        label='Город'
    )
    inn = forms.IntegerField(required=False, label='ИНН')
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(), required=False, label='Ведомство'
    )

    class Meta:
        model = Client
        fields = ['name', 'city', 'inn', 'department', 'view']


class StageBeginNameForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Этап подготовки')
    file = forms.BooleanField(
        initial=False, required=False, label='наличие отчетного документа'
    )

    class Meta:
        model = StageBeginName
        fields = ['name', 'file']


class StageMiddleNameForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Этап выполнения')
    file = forms.BooleanField(
        initial=False, required=False, label='наличие отчетного документа'
    )

    class Meta:
        model = StageMiddleName
        fields = ['name', 'file']


class StageEndNameForm(ViewField):
    name = forms.CharField(max_length=MAX_LENGTH,
                           help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                           label='Этап завершения')
    file = forms.BooleanField(
        initial=False, required=False, label='наличие отчетного документа'
    )

    class Meta:
        model = StageEndName
        fields = ['name', 'file']


class EmployeeForm(ViewField):
    last_name = forms.CharField(
        max_length=MAX_LENGTH, help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator], label='Фамилия'
    )
    first_name = forms.CharField(
        max_length=MAX_LENGTH, help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator], label='Имя'
    )
    middle_name = forms.CharField(
        max_length=MAX_LENGTH, help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        validators=[cyrillic_validator], label='Отчество'
    )
    tabel = forms.IntegerField(min_value=0, label='табельный номер')
    norma = forms.CharField(max_length=MAX_LENGTH,
                            help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
                            label='норма часов')
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(), required=False, label='Подразделение'
    )
    # sub_division = forms.ModelChoiceField(
    #     queryset=SubDivision.objects.all(), required=False, label='Субподразделение'
    # )
    post = forms.ModelChoiceField(
        queryset=Post.objects.all(), required=False, label='Должность'
    )
    getdoc = forms.BooleanField(
        initial=False, required=False, label='Выдающий',
        help_text="Право на выдачу документов",
    )

    class Meta:
        model = Employee
        fields = [
            'last_name', 'first_name', 'middle_name', 'tabel', 'norma',
            'division', 'post', 'getdoc', 'view',
        ]
        readonly_fields = ()

