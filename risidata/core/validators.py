from django.core.validators import RegexValidator

# Создание валидатора с регулярным выражением, которое проверяет наличие
# только строчных и прописных кириллических символов.
cyrillic_validator = RegexValidator(
    regex=r'^[А-Яа-яЁё-]+$',
    message='Допускается вводить только символы кириллицы и -',
    code='invalid_cyrillic',
)
