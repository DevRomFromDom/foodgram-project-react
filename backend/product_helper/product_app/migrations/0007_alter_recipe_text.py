# Generated by Django 3.2 on 2022-10-18 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0006_alter_ingredientamount_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(help_text='Описание рецепта', max_length=20000, verbose_name='Описание'),
        ),
    ]
