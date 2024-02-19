from django.contrib import admin

from database.models import (
    Post,
    Division,
    # SubDivision,
    ConditionContract,
    StatusContract,
    # ControlPrice,
    Department,
    Client,
    StageBeginName,
    StageMiddleName,
    StageEndName,
    Employee,
)


MODELS = [
    Division,
    ConditionContract,
    StatusContract,
    # ControlPrice,
    Department,
]

for model in MODELS:
    model_name = model.__name__

    # Создание класса модели администратора
    admin_class_name = f"{model_name}Admin"
    admin_class_dict = {
        'fields': ('id', 'name', 'view', 'last_change'),
        'list_display': ('id', 'name', 'view'),
        'list_editable': ('name', 'view'),
        'readonly_fields': ('id', 'last_change'),
        'list_filter': ('view',),
        'search_fields': ('name',)
    }
    admin_class = type(admin_class_name, (admin.ModelAdmin,), admin_class_dict)

    # Регистрация модели и класса администратора
    admin.site.register(model, admin_class)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'abbr', 'view', 'last_change')
    list_display = ('id', 'name', 'abbr', 'view')
    list_editable = ('name', 'abbr', 'view')
    readonly_fields = ('id', 'last_change')
    list_filter = ('view',)
    search_fields = ('name',)


# @admin.register(SubDivision)
# class SubDivisionAdmin(admin.ModelAdmin):
#     fields = ('id', 'division', 'name', 'view', 'date_create', 'date_update', 'user_create', 'user_update', 'last_change')
#     list_display = ('id', 'division', 'name', 'view')
#     list_editable = ('division', 'name', 'view')
#     readonly_fields = ('id', 'date_create', 'date_update', 'user_create', 'user_update', 'last_change')
#     list_filter = ('division', 'view',)
#     search_fields = ('name',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'city', 'inn', 'department',
              'view', 'last_change')
    list_display = ('id', 'name', 'city', 'inn', 'department', 'view')
    list_editable = ('name', 'city', 'inn', 'department', 'view')
    readonly_fields = ('id', 'last_change')
    list_filter = ('city', 'department', 'view')
    search_fields = ('name',)


@admin.register(StageBeginName)
class StageBeginNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'file')
    list_editable = ('name', 'file')


@admin.register(StageMiddleName)
class StageMiddleNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name',)


@admin.register(StageEndName)
class StageEndNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    fields = (
        'first_name', 'last_name', 'middle_name', 'tabel', 'norma',
        'post', 'division', 'getdoc', 'view',
    )
    list_display = ('__str__', 'post', 'division', 'getdoc', 'view',)
    list_editable = ('post', 'division', 'view',)
    readonly_fields = ()
    list_filter = ('post', 'division', 'getdoc', 'view',)
    search_fields = ('first_name', 'last_name', 'middle_name')
