# Generated by Django 2.1.5 on 2024-02-02 11:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0008_page_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='likes',
        ),
    ]