# Generated by Django 3.2.16 on 2024-05-02 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='text',
            field=models.TextField(default=None, verbose_name='Текст комментария'),
            preserve_default=False,
        ),
    ]
