from django import forms


class UserSettingsForm(forms.Form):
    """Форма настройки списка объекта"""

    def __init__(
            self,
            choices=(),
            settings=None,
            count_columns=1,
            first_column=None,
            *args,
            **kwargs,
    ):
        self.count_columns = self.check_count(count_columns)
        super().__init__(*args, **kwargs)
        if settings is None:
            settings = []
        for column_index in range(1, self.count_columns + 1):
            field_name = f'column_{column_index}'
            label_text = f'Столбец {column_index}'
            try:
                value = settings[column_index - 1]
            except (IndexError, TypeError):
                value = ''
            default = {
                'choices': choices,
                'label': label_text,
                'required': False,
                'initial': value,
            }
            if first_column and column_index == 1:
                default.update(
                    disabled=True,
                    help_text='изменять нельзя',
                    initial=first_column,
                )
            self.fields[field_name] = forms.ChoiceField(**default)

    def check_count(self, count):
        if not isinstance(count, int) or count < 1:
            raise TypeError('The number of fields must be a positive integer')
        return count

    def clean(self):
        cleaned_data = super().clean()
        field_duplicates = [
            field
            for field, value in cleaned_data.items()
            if value and list(cleaned_data.values()).count(value) > 1
        ]
        for field in field_duplicates:
            self.add_error(field, 'Значения столбцов должны быть уникальными.')

        return cleaned_data
