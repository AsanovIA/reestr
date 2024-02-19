# Generated by Django 3.2.19 on 2023-10-12 10:25

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('number', models.CharField(blank=True, db_index=True, max_length=255, verbose_name='Номер')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата')),
                ('eosdo', models.CharField(blank=True, max_length=255, verbose_name='Номер в ЕОСДО')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Наименование')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('concurs', models.BooleanField(default=False, verbose_name='Конкурсная процедура')),
                ('guarantee_letter', models.BooleanField(default=False, verbose_name='Гарантийное письмо')),
                ('closed', models.BooleanField(default=False, verbose_name='Договор закрыт')),
                ('num_ng', models.IntegerField(blank=True, null=True, verbose_name='Номер номенклатурной группы')),
                ('num_stage', models.IntegerField(blank=True, null=True, verbose_name='Номер этапа')),
                ('igk', models.CharField(blank=True, max_length=255, verbose_name='ИГК')),
                ('date_begin', models.DateField(blank=True, null=True, verbose_name='Дата начала работ')),
                ('date_end_plan', models.DateField(blank=True, null=True, verbose_name='Дата окончания - план')),
                ('date_end_prognoz', models.DateField(blank=True, null=True, verbose_name='Дата окончания - прогноз')),
                ('date_end_fact', models.DateField(blank=True, null=True, verbose_name='Дата окончания - факт')),
                ('control_price', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'с ценообразованием'), (2, 'без ценообразования'), (3, 'без контроля')], null=True, verbose_name='Контроль военного представительства')),
                ('city', models.CharField(blank=True, max_length=255, verbose_name='Город')),
                ('inn', models.CharField(blank=True, max_length=255, verbose_name='ИНН')),
                ('department', models.CharField(blank=True, max_length=255, verbose_name='Ведомство')),
                ('great_department', models.CharField(blank=True, max_length=255, verbose_name='Ведомство головного исполнителя')),
                ('general_client', models.CharField(blank=True, max_length=255, verbose_name='Генеральный заказчик')),
                ('price_no_nds', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Цена без НДС, руб')),
                ('nds', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='НДС, %')),
                ('price_plus_nds', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Цена с НДС, руб')),
                ('summ_nds', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='НДС, руб')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='client', to='database.client', verbose_name='Заказчик')),
                ('condition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='database.conditioncontract', verbose_name='Состояние договора')),
                ('great_client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='greet_client', to='database.client', verbose_name='Головной исполнитель')),
            ],
            options={
                'verbose_name': 'договор',
                'verbose_name_plural': 'договора',
                'permissions': [('close_contract', 'Can close Договор')],
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('function', models.TextField(blank=True, max_length=1000, verbose_name='Функции')),
                ('otvetstvenny', models.BooleanField(blank=True, default=False, verbose_name='Ответственный')),
                ('ispolnitel', models.BooleanField(blank=True, default=False, verbose_name='Исполниттель')),
                ('soprovojdenie', models.BooleanField(blank=True, default=False, verbose_name='Сопровождение')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Договор')),
                ('employee', models.ForeignKey(blank=True, limit_choices_to={'view': True}, null=True, on_delete=django.db.models.deletion.PROTECT, to='database.employee', verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name': 'задействованный сотрудник',
                'verbose_name_plural': 'задействованные сотрудники',
            },
        ),
        migrations.CreateModel(
            name='TimeWork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('date', models.DateField(blank=True, db_index=True, null=True, verbose_name='Дата')),
                ('time', models.DecimalField(blank=True, decimal_places=1, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(24)], verbose_name='Время')),
                ('contract', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Проект')),
                ('name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contract.member', verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name': 'Время работы',
                'verbose_name_plural': 'Время работы',
            },
        ),
        migrations.CreateModel(
            name='StageMiddleList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('date_end_plan', models.DateField(blank=True, null=True, verbose_name='Срок - по договору')),
                ('plan', models.CharField(blank=True, max_length=255, verbose_name='План')),
                ('fact', models.CharField(blank=True, max_length=255, verbose_name='Факт')),
                ('date_end_prognoz', models.DateField(blank=True, null=True, verbose_name='Срок - прогноз')),
                ('date_end_fact', models.DateField(blank=True, null=True, verbose_name='Срок - факт')),
                ('number', models.CharField(blank=True, max_length=255, verbose_name='Номер')),
                ('file', models.FileField(blank=True, null=True, upload_to='document/', verbose_name='файл')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Договор')),
                ('ispolnitel', models.ForeignKey(blank=True, limit_choices_to={'ispolnitel': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ispolnitel_stage_middle', to='contract.member', verbose_name='Исполнитель')),
                ('name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='database.stagemiddlename', verbose_name='Навзвание')),
            ],
            options={
                'verbose_name': 'этап выполнения',
                'verbose_name_plural': 'этапы выполнения',
            },
        ),
        migrations.CreateModel(
            name='StageEndList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('date_end_plan', models.DateField(blank=True, null=True, verbose_name='Срок - по договору')),
                ('kolichestvo', models.CharField(blank=True, max_length=255, verbose_name='Количество')),
                ('gotov', models.CharField(blank=True, max_length=255, verbose_name='Готовность')),
                ('date_end_prognoz', models.DateField(blank=True, null=True, verbose_name='Срок - прогноз')),
                ('date_end_fact', models.DateField(blank=True, null=True, verbose_name='Срок - факт')),
                ('number', models.CharField(blank=True, max_length=255, verbose_name='Номер')),
                ('file', models.FileField(blank=True, null=True, upload_to='document/', verbose_name='Файл')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Договор')),
                ('ispolnitel', models.ForeignKey(blank=True, limit_choices_to={'ispolnitel': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ispolnitel_stage_end', to='contract.member', verbose_name='Исполнитель')),
                ('name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='database.stageendname', verbose_name='Навзвание')),
            ],
            options={
                'verbose_name': 'этап завершения',
                'verbose_name_plural': 'этапы завершения',
            },
        ),
        migrations.CreateModel(
            name='StageBeginList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('date_end_plan', models.DateField(blank=True, null=True, verbose_name='Срок - по договору')),
                ('kolichestvo', models.CharField(blank=True, max_length=255, verbose_name='Количество')),
                ('gotov', models.CharField(blank=True, max_length=255, verbose_name='Готовность')),
                ('date_end_prognoz', models.DateField(blank=True, null=True, verbose_name='Срок - прогноз')),
                ('date_end_fact', models.DateField(blank=True, null=True, verbose_name='Срок - факт')),
                ('number', models.CharField(blank=True, max_length=255, verbose_name='Номер')),
                ('file', models.FileField(blank=True, null=True, upload_to='document/', verbose_name='Файл')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Договор')),
                ('ispolnitel', models.ForeignKey(blank=True, limit_choices_to={'ispolnitel': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ispolnitel_stage_begin', to='contract.member', verbose_name='Исполнитель')),
                ('name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='database.stagebeginname', verbose_name='Навзвание')),
            ],
            options={
                'verbose_name': 'этап подготовки',
                'verbose_name_plural': 'этапы подготовки',
            },
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('number', models.CharField(blank=True, db_index=True, max_length=255, verbose_name='Номер')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'входящее'), (2, 'исходящее')], null=True, verbose_name='Статус')),
                ('content', models.TextField(blank=True, max_length=1000, verbose_name='Содержание')),
                ('file', models.FileField(blank=True, upload_to='document/', verbose_name='Файл')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Договор')),
                ('ispolnitel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contract.member', verbose_name='Исполнитель')),
            ],
            options={
                'verbose_name': 'письмо',
                'verbose_name_plural': 'письма',
            },
        ),
        migrations.AddField(
            model_name='contract',
            name='otvetstvenny',
            field=models.ForeignKey(blank=True, limit_choices_to={'otvetstvenny': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employeemember_otvetstvenny', to='contract.member', verbose_name='Ответственный'),
        ),
        migrations.AddField(
            model_name='contract',
            name='soprovojdenie',
            field=models.ForeignKey(blank=True, limit_choices_to={'soprovojdenie': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employeemember_soprovojdenie', to='contract.member', verbose_name='Сопровождение'),
        ),
        migrations.AddField(
            model_name='contract',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='database.statuscontract', verbose_name='Статус договора'),
        ),
        migrations.CreateModel(
            name='Calculation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('matzatrall', models.CharField(blank=True, max_length=255, verbose_name='Материальные затраты')),
                ('zarpall', models.CharField(blank=True, max_length=255, verbose_name='Затраты на зарплату')),
                ('proizvzatr', models.CharField(blank=True, max_length=255, verbose_name='Производственые затрыты')),
                ('zatrkomandir', models.CharField(blank=True, max_length=255, verbose_name='Затраты на командировки')),
                ('contract', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Договор')),
            ],
            options={
                'verbose_name': 'калькуляция',
                'verbose_name_plural': 'калькуляция',
            },
        ),
        migrations.CreateModel(
            name='AddAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change', models.TextField(blank=True, verbose_name='Последнее действие')),
                ('number', models.CharField(blank=True, db_index=True, max_length=255, verbose_name='Номер')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата')),
                ('comment', models.TextField(blank=True, max_length=1000, verbose_name='Комментарии')),
                ('file', models.FileField(blank=True, upload_to='document/', verbose_name='Файл')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='Договор')),
            ],
            options={
                'verbose_name': 'дополнительное соглашение',
                'verbose_name_plural': 'дополнительные соглашения',
            },
        ),
    ]
