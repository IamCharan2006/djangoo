# Generated by Django 5.1.2 on 2024-12-04 18:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0005_restaurant'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Restaurant',
        ),
    ]