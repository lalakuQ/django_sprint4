# Generated by Django 3.2.16 on 2024-04-08 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20240408_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='is_published',
            field=models.BooleanField(default=True, help_text='Снимите галочку,\n                                       чтобы скрыть публикацию.', verbose_name='Опубликовано'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(help_text='Идентификатор страницы для URL;\n                   разрешены символы латиницы, цифры, дефис\n                   и подчёркивание.', unique=True, verbose_name='Идентификатор'),
        ),
        migrations.AlterField(
            model_name='location',
            name='is_published',
            field=models.BooleanField(default=True, help_text='Снимите галочку,\n                                       чтобы скрыть публикацию.', verbose_name='Опубликовано'),
        ),
        migrations.AlterField(
            model_name='post',
            name='is_published',
            field=models.BooleanField(default=True, help_text='Снимите галочку,\n                                       чтобы скрыть публикацию.', verbose_name='Опубликовано'),
        ),
    ]
