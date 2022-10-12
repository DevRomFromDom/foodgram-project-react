from django.core.validators import RegexValidator


def username_validator(value):
    RegexValidator(
        r'^[\w.@+-]+$',
        message="Может содержать только буквы, "
        "цифры либо символы: '@', '.', '+', '-', '_'",
        code='Некорректное имя позльзователя'
    )(value=value)


def slug_validator(value):
    RegexValidator(
        r'^[-a-zA-Z0-9_]+$',
        message="Может содержать только буквы и цыфры, "
        "цифры либо символы: '-', '_'",
        code='Некорректное имя позльзователя'
    )(value=value)
