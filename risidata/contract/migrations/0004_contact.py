# Generated by Django 4.2.1 on 2023-10-15 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0003_alter_member_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('first_name', models.CharField(max_length=150, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=150, verbose_name='Фамилия')),
                ('middle_name', models.CharField(max_length=150, verbose_name='Отчество')),
                ('post', models.CharField(blank=True, max_length=150, verbose_name='Должность')),
                ('division', models.CharField(blank=True, max_length=150, verbose_name='Подразделение')),
                ('telephone', models.CharField(blank=True, max_length=150, verbose_name='Телефон')),
                ('email', models.CharField(blank=True, max_length=150, verbose_name='Адрес электронной почты')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Договор')),
            ],
            options={
                'verbose_name': 'контакт',
                'verbose_name_plural': 'контакты',
            },
        ),
    ]
