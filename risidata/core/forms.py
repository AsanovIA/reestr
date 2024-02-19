from django import forms

HELP_VIEW = ('Отметьте, если значение должно отображаться в списке выбора. '
             'Уберите эту отметку вместо удаления значения.')
LABEL_VIEW = 'Отображение'
MAX_LENGTH = 50
HELP_MAX_SYMBOL = 'Не более %s символов.'
HELP_AUTOFILL = 'Заполняется автоматически'
HELP_FILTER_HORIZONTAL = ('Удерживайте “Control“ (или “Command“ на Mac), '
                          'чтобы выбрать несколько значений.')


class ViewField(forms.ModelForm):
    view = forms.BooleanField(
        initial=True, required=False, help_text=HELP_VIEW, label=LABEL_VIEW
    )

    class Meta:
        abstract = True
