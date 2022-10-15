from django.core.validators import RegexValidator


def username_validator(value):
    """Валидатор для пользователя, поле username."""
    RegexValidator(
        r'^[\w.@+-]+$',
        message="Может содержать только буквы, "
        "цифры либо символы: '@', '.', '+', '-', '_'",
        code='Некорректное имя пользователя.'
    )(value=value)


def hex_color_validator(value):
    """Валидатор для цвета, типа HEX."""
    RegexValidator(
        r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message="Может содержать только буквы и цыфры, "
        "начинаться с '#' и быть длинной 6 или 3 символа, после '#'",
        code='Переданый цвет не типа HEX.'
    )(value=value)
