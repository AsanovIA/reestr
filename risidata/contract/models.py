from django.db import models

from core.models import GeneralModel, NAME_EMPTY
from core.utils import get_slug_url, try_get_url
from database.models import (
    StageBeginName,
    StageMiddleName,
    StageEndName,
    ConditionContract,
    StatusContract,
    # ControlPrice,
    Client,
    Employee,
)

WITH_PRICING = INCOMING = 1
WITHOUT_PRICING = OUTGOING = 2
WITHOUT_CONTROL = 3

choices_contract_control_price = [
    (WITH_PRICING, 'с ценообразованием'),
    (WITHOUT_PRICING, 'без ценообразования'),
    (WITHOUT_CONTROL, 'без контроля'),
]
choices_letter_status = [
    (INCOMING, 'входящее'),
    (OUTGOING, 'исходящее'),
]


class ContractRelated(GeneralModel):
    class Meta:
        abstract = True

    def get_absolute_url(self):
        app_label = self._meta.app_label
        urlargs = {
            'slug': get_slug_url({}, self._meta.model_name, obj_id=self.id,
                                 related_id=self.contract_id),
            'current_app': app_label,
        }
        return try_get_url(f'{app_label}_change', **urlargs)


class Member(ContractRelated):
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE,
                                 verbose_name='Договор')
    employee = models.ForeignKey(
        Employee,
        limit_choices_to={'view': True},
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Сотрудник',
    )
    function = models.TextField('Функции', blank=True, max_length=1000)
    otvetstvenny = models.BooleanField(default=False, blank=True,
                                       verbose_name='Ответственный')
    ispolnitel = models.BooleanField(default=False, blank=True,
                                     verbose_name='Исполниттель')
    soprovojdenie = models.BooleanField(default=False, blank=True,
                                        verbose_name='Сопровождение')

    class Meta:
        verbose_name = 'задействованный сотрудник'
        verbose_name_plural = 'задействованные сотрудники'

    def __str__(self):
        return str(self.employee)


class Contract(GeneralModel):
    number = models.CharField(
        'Номер', max_length=255, db_index=True, blank=True
    )
    date = models.DateField('Дата', blank=True, null=True)
    eosdo = models.CharField('Номер в ЕОСДО', max_length=255, blank=True)
    title = models.CharField('Наименование', max_length=255, blank=True)
    comment = models.TextField('Комментарий', blank=True)
    condition = models.ForeignKey(
        ConditionContract,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Состояние договора',
    )
    concurs = models.BooleanField('Конкурсная процедура', default=False)
    guarantee_letter = models.BooleanField('Гарантийное письмо', default=False)
    closed = models.BooleanField('Договор закрыт', default=False)
    status = models.ForeignKey(
        StatusContract,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Статус договора',
    )
    soprovojdenie = models.ForeignKey(
        Member,
        limit_choices_to={'soprovojdenie': True},
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Сопровождение',
        related_name='employeemember_soprovojdenie',
    )
    otvetstvenny = models.ForeignKey(
        Member,
        limit_choices_to={'otvetstvenny': True},
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Ответственный',
        related_name='employeemember_otvetstvenny',
    )
    num_ng = models.IntegerField(blank=True, null=True,
                                 verbose_name='Номер номенклатурной группы')
    num_stage = models.IntegerField(blank=True, null=True,
                                    verbose_name='Номер этапа')
    igk = models.CharField('ИГК', max_length=255, blank=True)
    date_begin = models.DateField('Дата начала работ', blank=True, null=True)
    date_end_plan = models.DateField(
        'Дата окончания - план', blank=True, null=True
    )
    date_end_prognoz = models.DateField(
        'Дата окончания - прогноз', blank=True, null=True
    )
    date_end_fact = models.DateField(
        'Дата окончания - факт', blank=True, null=True
    )
    control_price = models.PositiveSmallIntegerField(
        'Контроль военного представительства',
        choices=choices_contract_control_price,
        blank=True,
        null=True,
    )
    # control_price = models.ForeignKey(
    #     ControlPrice,
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    #     verbose_name='Контроль военного представительства',
    # )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Заказчик',
        related_name='client',
    )
    city = models.CharField(max_length=255, blank=True, verbose_name='Город')
    inn = models.CharField(max_length=255, blank=True, verbose_name='ИНН')
    department = models.CharField(max_length=255, blank=True,
                                  verbose_name='Ведомство')
    great_client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Головной исполнитель',
        related_name='greet_client',
    )
    great_department = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Ведомство головного исполнителя',
    )
    general_client = models.CharField(max_length=255, blank=True,
                                      verbose_name='Генеральный заказчик')
    price_no_nds = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, blank=True, null=True,
        verbose_name='Цена без НДС, руб'
    )
    nds = models.PositiveSmallIntegerField(
        blank=True, default=0, null=True, verbose_name='НДС, %'
    )
    price_plus_nds = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, blank=True, null=True,
        verbose_name='Цена с НДС, руб'
    )
    summ_nds = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, blank=True, null=True,
        verbose_name='НДС, руб'
    )

    class Meta:
        verbose_name = 'договор'
        verbose_name_plural = 'договора'
        permissions = [
            ("close_contract", "Can close Договор"),
        ]

    def save(self, *args, **kwargs):
        created = not self.pk  # Проверяем, создается ли новая запись
        super().save(*args, **kwargs)
        if created:
            # Добавление форм подразделов
            for f in self._meta.related_objects:
                if isinstance(f, models.OneToOneRel):
                    model = f.related_model
                    model.objects.create(contract_id=self.pk)


class Calculation(ContractRelated):
    contract = models.OneToOneField(
        Contract, on_delete=models.CASCADE, verbose_name='Договор'
    )
    matzatrall = models.CharField(max_length=255, blank=True,
                                  verbose_name='Материальные затраты')
    zarpall = models.CharField(max_length=255, blank=True,
                               verbose_name='Затраты на зарплату')
    proizvzatr = models.CharField(max_length=255, blank=True,
                                  verbose_name='Производственые затрыты')
    zatrkomandir = models.CharField(max_length=255, blank=True,
                                    verbose_name='Затраты на командировки')

    name_suffix = 'а'

    class Meta:
        verbose_name = 'калькуляция'
        verbose_name_plural = 'калькуляция'

    def __str__(self):
        return 'Калькуляция договора %s' % self.contract


class StageBeginList(ContractRelated):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
                                 verbose_name='Договор')
    name = models.ForeignKey(
        StageBeginName,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Навзвание',
    )
    ispolnitel = models.ForeignKey(
        Member,
        limit_choices_to={'ispolnitel': True},
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Исполнитель',
        related_name='ispolnitel_stage_begin',
    )
    date_end_plan = models.DateField(blank=True, null=True,
                                     verbose_name='Срок - по договору')
    kolichestvo = models.CharField(max_length=255, blank=True,
                                   verbose_name='Количество')
    gotov = models.CharField(max_length=255, blank=True,
                             verbose_name='Готовность')
    date_end_prognoz = models.DateField(blank=True, null=True,
                                        verbose_name='Срок - прогноз')
    date_end_fact = models.DateField(blank=True, null=True,
                                     verbose_name='Срок - факт')
    number = models.CharField(max_length=255, blank=True, verbose_name='Номер')
    file = models.FileField(upload_to='document/', blank=True, null=True,
                            verbose_name='Файл')

    class Meta:
        verbose_name = 'этап подготовки'
        verbose_name_plural = 'этапы подготовки'


class StageMiddleList(ContractRelated):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
                                 verbose_name='Договор')
    name = models.ForeignKey(
        StageMiddleName,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Навзвание',
    )
    ispolnitel = models.ForeignKey(
        Member,
        limit_choices_to={'ispolnitel': True},
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Исполнитель',
        related_name='ispolnitel_stage_middle'
    )
    date_end_plan = models.DateField(blank=True, null=True,
                                     verbose_name='Срок - по договору')
    plan = models.CharField(max_length=255, blank=True, verbose_name='План')
    fact = models.CharField(max_length=255, blank=True, verbose_name='Факт')
    date_end_prognoz = models.DateField(blank=True, null=True,
                                        verbose_name='Срок - прогноз')
    date_end_fact = models.DateField(blank=True, null=True,
                                     verbose_name='Срок - факт')
    number = models.CharField(max_length=255, blank=True, verbose_name='Номер')
    file = models.FileField(upload_to='document/', blank=True, null=True,
                            verbose_name='файл')

    class Meta:
        verbose_name = 'этап выполнения'
        verbose_name_plural = 'этапы выполнения'


class StageEndList(ContractRelated):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
                                 verbose_name='Договор')
    name = models.ForeignKey(
        StageEndName,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Навзвание',
    )
    ispolnitel = models.ForeignKey(
        Member,
        limit_choices_to={'ispolnitel': True},
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Исполнитель',
        related_name='ispolnitel_stage_end',
    )
    date_end_plan = models.DateField(blank=True, null=True,
                                     verbose_name='Срок - по договору')
    kolichestvo = models.CharField(max_length=255, blank=True,
                                   verbose_name='Количество')
    gotov = models.CharField(max_length=255, blank=True,
                             verbose_name='Готовность')
    date_end_prognoz = models.DateField(blank=True, null=True,
                                        verbose_name='Срок - прогноз')
    date_end_fact = models.DateField(blank=True, null=True,
                                     verbose_name='Срок - факт')
    number = models.CharField(max_length=255, blank=True, verbose_name='Номер')
    file = models.FileField(upload_to='document/', blank=True, null=True,
                            verbose_name='Файл')

    class Meta:
        verbose_name = 'этап завершения'
        verbose_name_plural = 'этапы завершения'


class Letter(ContractRelated):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
                                 verbose_name='Договор')
    number = models.CharField('Номер', max_length=255, db_index=True,
                              blank=True)
    date = models.DateField('Дата', blank=True, null=True)
    ispolnitel = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Исполнитель',
    )
    status = models.PositiveSmallIntegerField(
        'Статус', null=True, choices=choices_letter_status
    )
    content = models.TextField('Содержание', blank=True, max_length=1000)
    file = models.FileField(upload_to='document/', blank=True,
                            verbose_name='Файл')

    name_suffix = 'о'

    class Meta:
        verbose_name = 'письмо'
        verbose_name_plural = 'письма'

    # class Letter(models.Model): # Динамические пути хранения
    #     number = models.CharField(max_length=255)
    #     content = models.TextField()
    #     file = models.FileField(upload_to=upload_file_path)  # Изменено здесь
    #
    #     def upload_file_path(instance, filename):  # Новая функция
    #         return 'document/letter_{0}/{1}'.format(instance.id, filename)


class AddAgreement(ContractRelated):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
                                 verbose_name='Договор')
    number = models.CharField('Номер', max_length=255, db_index=True,
                              blank=True)
    date = models.DateField(blank=True, null=True, verbose_name='Дата')
    comment = models.TextField('Комментарий', blank=True, max_length=1000)
    file = models.FileField(upload_to='document/', blank=True,
                            verbose_name='Файл')

    name_suffix = 'о'
    verbose_name_short = 'доп. соглашение'
    verbose_name_plural_short = 'доп. соглашения'

    class Meta:
        verbose_name = 'дополнительное соглашение'
        verbose_name_plural = 'дополнительные соглашения'


class Contact(ContractRelated):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
                                 verbose_name='Договор')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, verbose_name='Отчество')
    comment = models.TextField('Комментарий', blank=True, max_length=1000)
    post = models.CharField(max_length=150, blank=True,
                            verbose_name='Должность')
    division = models.CharField(max_length=150, blank=True,
                                verbose_name='Подразделение')
    telephone = models.CharField(max_length=150, blank=True,
                                 verbose_name='Телефон')
    email = models.CharField(max_length=150, blank=True,
                             verbose_name='Адрес электронной почты')

    class Meta:
        verbose_name = 'контакт'
        verbose_name_plural = 'контакты'

    def __str__(self):
        name = self.get_full_name()
        return name if name else NAME_EMPTY

    def name(self):
        return self.get_full_name()

    name.short_description = 'Ф.И.О.'

    def get_full_name(self):
        full_name = "%s %s %s" % (self.last_name,
                                  self.first_name,
                                  self.middle_name
                                  )
        return full_name.strip()

    def get_short_name(self):
        try:
            short_name = '%s %s.%s.' % (str(self.last_name).capitalize(),
                                        str(self.first_name)[0].upper(),
                                        str(self.middle_name)[0].upper(),
                                        )
        except IndexError:
            return str(self.last_name).capitalize()

        return short_name


class TimeWork(ContractRelated):
    from django.core.validators import MinValueValidator, MaxValueValidator

    date = models.DateField(blank=True, null=True, db_index=True,
                            verbose_name='Дата')
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Сотрудник',
    )
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
                                 blank=True, null=True, verbose_name='Проект')
    time = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, verbose_name='Время',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(24),
        ]
    )

    name_suffix = 'о'

    class Meta:
        verbose_name = 'Время работы'
        verbose_name_plural = 'Время работы'

    def __str__(self):
        return str(self.contract)
