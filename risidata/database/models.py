from django.db import models

from core.models import ViewGeneralModel


class Post(ViewGeneralModel):
    name = models.CharField('Должность', max_length=200, unique=True)
    abbr = models.CharField('Должность сокращенно', max_length=200)

    name_suffix = 'а'

    class Meta:
        verbose_name = 'должность'
        verbose_name_plural = 'должности'


class Division(ViewGeneralModel):
    name = models.CharField('Подразделение', max_length=200, unique=True)

    name_suffix = 'о'

    class Meta:
        verbose_name = 'подразделение'
        verbose_name_plural = 'подразделения'


class SubDivision(ViewGeneralModel):
    name = models.CharField('Субподразделение', max_length=200, unique=True)
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        null=True,
        verbose_name='Подразделение',
    )

    name_suffix = 'о'

    class Meta:
        verbose_name = 'субподразделение'
        verbose_name_plural = 'субподразделения'


class ConditionContract(ViewGeneralModel):
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Состояние договора')

    name_suffix = 'о'

    class Meta:
        verbose_name = 'состояние договора'
        verbose_name_plural = 'состояния договора'


class StatusContract(ViewGeneralModel):
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Статус договора')

    class Meta:
        verbose_name = 'статус договора'
        verbose_name_plural = 'статусы договора'


class ControlPrice(ViewGeneralModel):
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Контроль ВП на ценообразование')

    class Meta:
        verbose_name = 'контроль цены'
        verbose_name_plural = 'контроль цены'


class Department(ViewGeneralModel):
    name = models.CharField('Ведомство', max_length=200, unique=True)

    class Meta:
        verbose_name = 'ведомство'
        verbose_name_plural = 'ведомства'


class Client(ViewGeneralModel):
    name = models.CharField(
        max_length=200, db_index=True, unique=True, verbose_name='Заказчик'
    )
    city = models.CharField(max_length=200, verbose_name='Город')
    inn = models.IntegerField(blank=True, null=True, verbose_name='ИНН')
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Ведомство',
    )
    getdoc = models.BooleanField(default=False, blank=True,
                                 verbose_name='Выдающий')

    class Meta:
        verbose_name = 'организация'
        verbose_name_plural = 'организации'


class StageBeginName(ViewGeneralModel):
    name = models.CharField(max_length=255, unique=True,
                            blank=True, verbose_name='Этап подготовки')
    file = models.BooleanField(default=False, blank=True,
                               verbose_name='наличие отчетного документа')

    class Meta:
        verbose_name = 'наименование этапа подготовки'
        verbose_name_plural = 'наименования этапов подготовки'


class StageMiddleName(ViewGeneralModel):
    name = models.CharField(max_length=255, unique=True,
                            blank=True, verbose_name='Этап выполнения')
    file = models.BooleanField(default=False, blank=True,
                               verbose_name='наличие отчетного документа')

    class Meta:
        verbose_name = 'наименование этапа выполнения'
        verbose_name_plural = 'наименования этапов выполнения'


class StageEndName(ViewGeneralModel):
    name = models.CharField(max_length=255, unique=True,
                            blank=True, verbose_name='Этап завершения')
    file = models.BooleanField(default=False, blank=True,
                               verbose_name='наличие отчетного документа')

    class Meta:
        verbose_name = 'наименование этапа завершения'
        verbose_name_plural = 'наименования этапов завершения'


class Employee(ViewGeneralModel):
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, verbose_name='Отчество')
    tabel = models.PositiveIntegerField(
        unique=True, blank=True, verbose_name='табельный номер'
    )
    norma = models.CharField(max_length=150, blank=True,
                             verbose_name='норма часов')
    post = models.ForeignKey(Post, on_delete=models.PROTECT, blank=True,
                             null=True, verbose_name='Должность')
    division = models.ForeignKey(
        Division, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Подразделение'
    )
    # sub_division = models.ForeignKey(
    #     SubDivision, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Субподразделение'
    # )
    getdoc = models.BooleanField(default=False, blank=True,
                                 verbose_name='Выдающий')

    class Meta:
        verbose_name = 'сотрудник'
        verbose_name_plural = 'сотрудники'

    def __str__(self):
        return self.get_short_name()

    def full_name(self):
        return self.get_full_name()

    full_name.short_description = 'Сотрудник'

    def post_abbr(self):
        return self.post.abbr if self.post else ''

    post_abbr.short_description = 'Должность сокращенно'

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
