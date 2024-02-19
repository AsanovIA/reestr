from django.db import models

from core.utils import get_slug_url, try_get_url

HELP_VIEW = ("Отметьте, если значение должно отображаться в списке выбора. "
             "Уберите эту отметку вместо удаления значения.")
NAME_EMPTY = 'без наименования'
NUMBER_EMPTY = 'без номера'


class GeneralModel(models.Model):
    # date_create = models.DateTimeField(
    #     auto_now_add=True,
    #     verbose_name='Дата добавления',
    # )
    # date_update = models.DateTimeField(
    #     auto_now=True,
    #     verbose_name='Дата изменения',
    # )
    # user_create = models.ForeignKey(
    #     AUTH_USER_MODEL,
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    #     verbose_name='Добавил',
    #     related_name='create_%(class)s',
    # )
    # user_update = models.ForeignKey(
    #     AUTH_USER_MODEL,
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    #     verbose_name='Изменил',
    #     related_name='update_%(class)s',
    # )
    last_change = models.TextField(
        blank=True, verbose_name='Последнее действие'
    )

    name_suffix = ''

    class Meta:
        abstract = True

    def __str__(self):
        if hasattr(self, 'name'):
            return str(self.name) if self.name else NAME_EMPTY
        else:
            return str(self.number) if self.number else NUMBER_EMPTY

    def get_absolute_url(self):
        app_label = self._meta.app_label
        urlargs = {
            'slug': get_slug_url({}, self._meta.model_name, self.id),
            'current_app': app_label,
        }
        return try_get_url(f'{app_label}_change', **urlargs)


class ViewGeneralModel(GeneralModel):
    view = models.BooleanField(default=True, help_text=HELP_VIEW,
                               verbose_name='Отображение')

    class Meta:
        abstract = True
