from django import forms
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import (
    AdminFileWidget,
    # FilteredSelectMultiple,
)
from django.db.models import Q

from core.forms import HELP_MAX_SYMBOL, MAX_LENGTH
from contract.models import (
    Contract, Member, Calculation,
    StageBeginList, StageMiddleList, StageEndList, Letter, AddAgreement,
    TimeWork, Contact,
)
from database.models import (
    Employee,
    StageBeginName, StageMiddleName, StageEndName,
    ConditionContract, StatusContract,
    # ControlPrice,
    Client,
)
from core.widgets import (
    FilteredSelectMultiple,
    DateWidget,
)


class ContractRelatedForm(forms.ModelForm):
    def __init__(self, contract_id, *args, **kwargs):
        self.contract_id = contract_id
        super().__init__(*args, **kwargs)


class ContractForm(forms.ModelForm):
    # from core.utils import EMPTY_LABEL
    # from .models import choices_contract_control_price
    #
    # choices_control_price = [(0, EMPTY_LABEL)] + choices_contract_control_price

    number = forms.CharField(
        max_length=MAX_LENGTH, help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        required=False, label='Номер договора',
    )
    date = forms.DateField(required=False, label='Дата', widget=DateWidget())
    eosdo = forms.CharField(
        max_length=MAX_LENGTH, help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        required=False, label='Номер в ЕОСДО',
    )
    title = forms.CharField(
        max_length=MAX_LENGTH, help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        required=False, label='Наименование',
    )
    comment = forms.CharField(
        max_length=500,
        help_text=HELP_MAX_SYMBOL % 500,
        required=False,
        label='Комментарий',
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 3}),
    )
    condition = forms.ModelChoiceField(
        queryset=ConditionContract.objects.all(),
        required=False,
        label='Состояние договора',
    )
    concurs = forms.BooleanField(
        initial=False, required=False, label='Конкурсная процедура'
    )
    guarantee_letter = forms.BooleanField(
        initial=False, required=False, label='Гарантийное письмо'
    )
    status = forms.ModelChoiceField(
        queryset=StatusContract.objects.all(),
        required=False,
        label='Статус договора',
    )
    soprovojdenie = forms.ModelChoiceField(
        queryset=Member.objects.none(), required=False, label='Сопровождение',
    )
    otvetstvenny = forms.ModelChoiceField(
        queryset=Member.objects.none(), required=False, label='Ответственный',
    )
    num_ng = forms.IntegerField(required=False,
                                label='Номер номенклатурной группы')
    num_stage = forms.IntegerField(required=False, label='Номер этапа')
    igk = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        required=False,
        label='ИГК'
    )
    date_begin = forms.DateField(
        required=False, widget=DateWidget(), label='Срок начала работ'
    )
    date_end_plan = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - план'
    )
    date_end_prognoz = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - прогноз'
    )
    date_end_fact = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - факт'
    )
    # control_price = forms.ChoiceField(
    #     choices=choices_control_price,
    #     required=False,
    #     label='Контроль военного представительства'
    # )
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label='Заказчик',
    )
    city = forms.CharField(max_length=255, required=False, label='Город')
    inn = forms.CharField(max_length=255, required=False, label='ИНН')
    department = forms.CharField(max_length=255, required=False,
                                 label='Ведомство')
    great_client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label='Головной исполнитель',
    )
    great_department = forms.CharField(
        max_length=255,
        required=False,
        label='Ведомство головного исполнителя',
    )
    general_client = forms.CharField(max_length=255, required=False,
                                     label='Генеральный заказчик')
    price_no_nds = forms.DecimalField(
        max_digits=11, decimal_places=2, required=False, initial=0,
        label='Цена без НДС, руб'
    )
    nds = forms.IntegerField(
        max_value=100, required=False, initial=20, label='НДС, %'
    )
    price_plus_nds = forms.DecimalField(
        max_digits=11, decimal_places=2, required=False, initial=0,
        label='Цена с НДС, руб.'
    )
    summ_nds = forms.DecimalField(
        max_digits=11, decimal_places=2, required=False, initial=0,
        label='НДС, руб.'
    )

    prepopulated_fields = {}

    class Meta:
        model = Contract
        fieldsets = (
            ('', {
                'fields': (
                    'number', 'date', 'eosdo', 'title', 'comment', 'condition',
                    'concurs', 'guarantee_letter', 'status', 'soprovojdenie',
                    'otvetstvenny', 'num_ng', 'num_stage', 'igk'
                )
            }),
            ('Даты выполнения', {
                'classes': ('collapse',),
                'fields': (
                    'date_begin', 'date_end_plan', 'date_end_prognoz',
                    'date_end_fact'
                )
            }),
            ('Заказчик', {
                'classes': ('collapse',),
                'fields': (
                    'control_price', ('client', 'city', 'inn', 'department'),
                    'great_client', 'great_department', 'general_client'
                )
            }),
            ('Стоимость', {
                'classes': ('collapse',),
                'fields': (
                    ('price_no_nds', 'nds'), ('price_plus_nds', 'summ_nds')
                )
            }),
        )
        fields = [
            'number', 'date', 'eosdo', 'title', 'comment', 'condition',
            'concurs',  'guarantee_letter', 'status', 'soprovojdenie',
            'otvetstvenny', 'num_ng', 'num_stage', 'igk',
            'date_begin', 'date_end_plan', 'date_end_prognoz', 'date_end_fact',
            'control_price', 'client', 'city', 'inn', 'department',
            'great_client', 'great_department', 'general_client',
            'price_no_nds', 'nds', 'price_plus_nds', 'summ_nds',
        ]
        add_fields = ['number', 'date', 'eosdo', 'num_ng', 'igk']
        readonly_fields = (
            'summ_nds', 'price_plus_nds', 'city', 'inn', 'department'
        )
        widgets = {
            'date': DateWidget(),
            'date_begin': DateWidget(),
            'date_end_plan': DateWidget(),
            'date_end_prognoz': DateWidget(),
            'date_end_fact': DateWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'instance') and self.instance.id:
            self.fields['soprovojdenie'].queryset = Member.objects.filter(
                contract_id=self.instance.id,
                soprovojdenie=True,
            ).select_related('employee',)
            self.fields['otvetstvenny'].queryset = Member.objects.filter(
                contract_id=self.instance.id,
                otvetstvenny=True,
            ).select_related('employee',)

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 10:
            raise ValidationError('Длина превышает 10 символов')
        return title

    def clean_number(self):
        number = self.cleaned_data['number']
        if len(number) > 10:
            raise ValidationError('Длина превышает 10 символов')
        return number


class CalculationForm(ContractRelatedForm):
    matzatrall = forms.CharField(max_length=255, required=False, label='Материальные затраты')
    zarpall = forms.CharField(max_length=255, required=False, label='Затраты на зарплату')
    proizvzatr = forms.CharField(max_length=255, required=False, label='Производственые затрыты')
    zatrkomandir = forms.CharField(max_length=255, required=False, label='Затраты на командировки')

    class Meta:
        model = Calculation
        fields = ['matzatrall', 'zarpall', 'proizvzatr', 'zatrkomandir']


class MemberForm(ContractRelatedForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(), label='Сотрудник',
    )
    # function = forms.CharField(
    #     max_length=500,
    #     help_text=HELP_MAX_SYMBOL % 500,
    #     required=False,
    #     label='Функции',
    #     widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}),
    # )
    otvetstvenny = forms.BooleanField(
        initial=False, required=False, label='Ответственный',
        help_text="Ответственный за договор",
    )
    ispolnitel = forms.BooleanField(
        initial=False, required=False, label='Исполнитель',
        help_text="Исполнитель этапа",
    )
    soprovojdenie = forms.BooleanField(
        initial=False, required=False, label='Сопровождение',
        help_text="Сопровождение договора",
    )

    class Meta:
        model = Member
        fields = ['employee', 'otvetstvenny', 'ispolnitel', 'soprovojdenie']
        add_fields = ['employee']
        readonly_fields = ('employee',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields['employee'].queryset = Employee.objects.exclude(
                Q(member__contract_id=self.contract_id) |
                Q(view=False),
            )

    def clean_employee(self):
        employee = self.cleaned_data.get('employee')
        if Member.objects.filter(
                contract_id=self.contract_id, employee=employee
        ).exists() and not self.instance.id:
            raise ValidationError('Этот сотрудник уже добавлен в список.')

        return employee


class StageAddForm(forms.Form):
    stage_begin = forms.ModelMultipleChoiceField(
        queryset=StageBeginName.objects.none(),
        widget=FilteredSelectMultiple(
            verbose_name='Этапы подготовки', is_stacked=False,
        ),
        required=False,
        label='Этапы подготовки'
    )
    stage_middle = forms.ModelMultipleChoiceField(
        queryset=StageMiddleName.objects.none(),
        widget=FilteredSelectMultiple(
            verbose_name='Этапы выполнения', is_stacked=False,
        ),
        required=False,
        label='Этапы выполнения'
    )
    stage_end = forms.ModelMultipleChoiceField(
        queryset=StageEndName.objects.none(),
        widget=FilteredSelectMultiple(
            verbose_name='Этапы завершения', is_stacked=False,
        ),
        required=False,
        label='Этапы завершения'
    )

    class Meta:
        fields = ['stage_begin', 'stage_middle', 'stage_end']

    def __init__(self, contract_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stage_begin'].queryset = StageBeginName.objects.exclude(
            stagebeginlist__contract_id=contract_id
        )
        self.fields['stage_middle'].queryset = StageMiddleName.objects.exclude(
            stagemiddlelist__contract_id=contract_id
        )
        self.fields['stage_end'].queryset = StageEndName.objects.exclude(
            stageendlist__contract_id=contract_id
        )


class StageBeginListForm(ContractRelatedForm):
    name = forms.ModelChoiceField(
        queryset=StageBeginName.objects.all(), required=False,
        label='Этапы подготовки',
    )
    ispolnitel = forms.ModelChoiceField(
        queryset=None, required=False, label='Исполнитель',
    )
    date_end_plan = forms.DateField(
        required=False,
        widget=DateWidget(),
        label='Срок окончания - по договору',
    )
    kolichestvo = forms.CharField(
        max_length=255, required=False, label='колличество'
    )
    gotov = forms.CharField(max_length=255, required=False, label='готовность')
    date_end_prognoz = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - прогноз'
    )
    date_end_fact = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - факт'
    )
    number = forms.CharField(max_length=255, required=False, label='номер')
    file = forms.FileField(required=False, label='файл')

    class Meta:
        model = StageBeginList
        fields = [
            'name', 'ispolnitel', 'date_end_plan', 'kolichestvo', 'gotov',
            'date_end_prognoz', 'date_end_fact', 'number', 'file',
        ]
        readonly_fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ispolnitel'].queryset = Member.objects.filter(
            contract_id=self.contract_id,
            ispolnitel=True,
        ).select_related('employee',)


class StageMiddleListForm(ContractRelatedForm):
    name = forms.ModelChoiceField(
        queryset=StageMiddleName.objects.all(), required=False,
        label='Этапы выполнения',
    )
    ispolnitel = forms.ModelChoiceField(
        queryset=None, required=False, label='Исполнитель',
    )
    date_end_plan = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - по договору'
    )
    plan = forms.CharField(max_length=255, required=False, label='план')
    fact = forms.CharField(max_length=255, required=False, label='факт')
    date_end_prognoz = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - прогноз'
    )
    date_end_fact = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - факт'
    )
    number = forms.CharField(max_length=255, required=False, label='номер')
    file = forms.FileField(required=False, label='файл')

    class Meta:
        model = StageMiddleList
        fields = [
            'name', 'ispolnitel', 'date_end_plan', 'plan', 'fact',
            'date_end_prognoz', 'date_end_fact', 'number', 'file',
        ]
        readonly_fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ispolnitel'].queryset = Member.objects.filter(
            contract_id=self.contract_id,
            ispolnitel=True,
        ).select_related('employee',)


class StageEndListForm(ContractRelatedForm):
    name = forms.ModelChoiceField(
        queryset=StageEndName.objects.all(), required=False,
        label='Этапы завершения',
    )
    ispolnitel = forms.ModelChoiceField(
        queryset=Member.objects.none(), required=False, label='Исполнитель',
    )
    date_end_plan = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - по договору'
    )
    kolichestvo = forms.CharField(
        max_length=255, required=False, label='колличество'
    )
    gotov = forms.CharField(max_length=255, required=False, label='готовность')
    date_end_prognoz = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - прогноз'
    )
    date_end_fact = forms.DateField(
        required=False, widget=DateWidget(), label='Срок окончания - факт'
    )
    number = forms.CharField(max_length=255, required=False, label='номер')
    file = forms.FileField(required=False, label='файл')

    class Meta:
        model = StageEndList
        fields = [
            'name', 'ispolnitel', 'date_end_plan', 'kolichestvo', 'gotov',
            'date_end_prognoz', 'date_end_fact', 'number', 'file',
        ]
        add_fields = ['name']
        readonly_fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['ispolnitel'].queryset = Member.objects.filter(
                contract_id=self.contract_id,
                ispolnitel=True,
            ).select_related('employee',)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if StageEndList.objects.filter(
                contract_id=self.contract_id, name=name
        ).exists() and not self.instance.id:
            raise ValidationError('Этот этап уже добавлен в список.')

        return name


class LetterForm(ContractRelatedForm):
    from core.utils import BLANK_CHOICE
    from .models import choices_letter_status

    choices_letter = BLANK_CHOICE + choices_letter_status

    number = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        required=False,
        label='Номер',
    )
    date = forms.DateField(required=False, label='Дата', widget=DateWidget())
    ispolnitel = forms.ModelChoiceField(
        queryset=Member.objects.none(),
        required=False,
        label='Исполнитель',
        help_text='Задействованный сотрудник',
    )
    content = forms.CharField(
        max_length=500,
        help_text=HELP_MAX_SYMBOL % 500,
        required=False,
        label='Содержание',
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 5}),
    )
    # file = forms.FileField(required=False, label='Письмо', widget=AdminFileWidget())

    class Meta:
        model = Letter
        # fieldsets = (
        #     ('номер дата', {
        #         'classes': ('collapse',),
        #         'fields': ('num_contract', ('number', 'date'))
        #     }),
        #     ('содержание', {
        #         'classes': ('collapse',),
        #         'fields': ('status', 'ispolnitel', 'content', 'file')
        #     }),
        # )
        fields = ['number', 'ispolnitel', 'date', 'status', 'content', 'file']
        widgets = {
            'date': DateWidget()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ispolnitel'].queryset = Member.objects.filter(
            contract_id=self.contract_id,
        ).select_related('employee',)


class AddAgreementForm(ContractRelatedForm):
    number = forms.CharField(
        max_length=MAX_LENGTH,
        help_text=HELP_MAX_SYMBOL % MAX_LENGTH,
        required=False,
        label='Номер соглашения',
    )
    date = forms.DateField(required=False, label='Дата', widget=DateWidget())
    comment = forms.CharField(
        max_length=500,
        help_text=HELP_MAX_SYMBOL % 500,
        required=False,
        label='Комментарий',
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}),
    )
    file = forms.FileField(required=False, label='Файл соглашения')

    class Meta:
        model = AddAgreement
        fields = ['number', 'date', 'comment', 'file']
        widgets = {
            'date': DateWidget()
        }


class ContactForm(ContractRelatedForm):
    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False,
                                label='Фамилия')
    middle_name = forms.CharField(max_length=150, required=False,
                                  label='Отчество')
    comment = forms.CharField(
        max_length=500,
        help_text=HELP_MAX_SYMBOL % 500,
        required=False,
        label='Комментарий',
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}),
    )
    post = forms.CharField(max_length=150, required=False, label='Должность')
    division = forms.CharField(max_length=150, required=False,
                               label='Подразделение')
    telephone = forms.CharField(max_length=150, required=False,
                                label='Телефон')
    email = forms.CharField(max_length=150, required=False,
                            label='Адрес электронной почты')

    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'middle_name', 'comment', 'post',
            'division', 'telephone', 'email'
        ]


class TimeWorkForm(forms.ModelForm):
    contract = forms.ModelChoiceField(
        queryset=Contract.objects.all(), label='Договор'
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(), label='Сотрудник',
    )
    date = forms.DateField(required=False, label='Дата', widget=DateWidget())
    time = forms.DecimalField(
        max_value=24, min_value=0, max_digits=3,  decimal_places=1,
        required=False, label='Часы'
    )

    class Meta:
        model = TimeWork
        fields = [
            'contract', 'employee', 'date', 'time'
        ]


class SetTimeWorkForm(forms.ModelForm):
    full_name = forms.CharField(max_length=MAX_LENGTH, required=False,
                                label='Сотрудник')
    tabel = forms.CharField(max_length=MAX_LENGTH, required=False,
                            label='Табельный номер')
    norma = forms.CharField(max_length=MAX_LENGTH, required=False,
                            label='Норма часов')
    date = forms.DateField(label='Дата', widget=DateWidget(
        attrs={"class": "vDateFieldRequest vDateField"}
    ))

    class Meta:
        model = Employee
        fieldsets = (
            ('', {'fields': (('full_name', 'tabel', 'norma'),)}),
            ('', {'fields': ('date',)}),
        )
        fields = ['full_name', 'tabel', 'norma', 'date']
        readonly_fields = ('full_name', 'tabel', 'norma')

