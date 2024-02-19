from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import Coalesce

from contract.models import (
    Contract,
    Calculation,
    StageBeginList,
    StageMiddleList,
    StageEndList,
    Letter,
    AddAgreement, TimeWork
)


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     save_on_top = True
#     fields = ('id', 'user', 'username', 'password', 'first_name', 'last_name', 'middle_name', 'name', 'email',
#               'post', 'post_abbr', 'division', 'sub_division', 'otvetstvenny', 'ispolnitel', 'soprovojdenie', 'getdoc',
#               'view', 'date_create', 'date_update', 'user_create', 'user_update', 'last_change')
#     list_display = ('id', 'sub_division', 'otvetstvenny', 'ispolnitel', 'soprovojdenie', 'getdoc', 'name', 'view')
#     list_editable = ('sub_division', 'otvetstvenny', 'ispolnitel', 'soprovojdenie', 'getdoc', 'name', 'view')
#     readonly_fields = ('id', 'user', 'name', 'date_create', 'date_update', 'user_create', 'user_update', 'last_change')
#     list_filter = ('division', 'view',)
#     search_fields = ('name',)


# # Создаем админскую форму
# class UserProfileForm(UserChangeForm):
#     class Meta:
#         model = UserProfile
#         fields = ('id', 'username', 'user', 'middle_name', 'name', 'post', 'post_abbr', 'division',
#                       'sub_division', 'otvetstvenny', 'ispolnitel', 'soprovojdenie', 'getdoc')



# # Регистрируем модель Userprofilel с админской формой
# class UserProfilelAdmin(admin.ModelAdmin):
#     form = UserProfileForm
#
#     list_display = ('id', 'sub_division', 'otvetstvenny', 'ispolnitel', 'soprovojdenie', 'getdoc', 'name', 'view')
#     list_editable = ('sub_division', 'otvetstvenny', 'ispolnitel', 'soprovojdenie', 'getdoc', 'name', 'view')
#     readonly_fields = ('id', 'name', 'date_create', 'date_update', 'user_create', 'user_update', 'last_change')
#     list_filter = ('division', 'view',)
#     search_fields = ('name',)


# # Зарегистрируем модель Userprofilel и User
# admin.site.register(UserProfile, UserProfilelAdmin)
# admin.site.unregister(User)  # Снимаем регистрацию User из стандартного админского интерфейса
# admin.site.register(User, UserAdmin) # Регистрируем User с его стандартной админской формой


class LetterInline(admin.StackedInline):
    model = Letter
    extra = 0
    fields = (
        'number', 'date', 'ispolnitel',
    )
    readonly_fields = ('contract', 'last_change')


class AddAgreementInline(admin.TabularInline):
    model = AddAgreement
    extra = 0


class ContractAdmin(admin.ModelAdmin):
    save_on_top = True
    # autocomplete_fields = ['condition'] # FK с поиском
    list_display = (
        'id', 'number', 'condition', 'title', 'client', 'status', 'closed'
    )
    list_display_links = ('id', 'number')
    list_editable = ('condition', 'status', 'closed')
    list_filter = ('condition', 'status', 'guarantee_letter', 'num_ng', 'date')
    search_fields = ('title', 'client__name')
    readonly_fields = ('city', 'inn', 'department', 'price_plus_nds', 'summ_nds')
    # list_per_page = 1
    inlines = [
        LetterInline,
        AddAgreementInline
    ]
    fieldsets = (
        ('', {
            'fields': (('number', 'date', 'eosdo'), 'title', 'comment',
                       'concurs', ('condition', 'closed', 'guarantee_letter'),
                       'status', ('soprovojdenie', 'otvetstvenny'), 'num_ng',
                       'num_stage', 'igk'
                       )
        }),
        ('Даты выполнения', {
            'classes': ('collapse',),
            'fields': ('date_begin', 'date_end_plan', 'date_end_prognoz', 'date_end_fact')
        }),
        ('Заказчик', {
            'classes': ('collapse',),
            'fields': ('control_price', ('client', 'city', 'inn', 'department'),
                       'great_client', 'great_department', 'general_client')
        }),
        ('Стоимость', {
            'classes': ('collapse',),
            'fields': (('price_no_nds', 'nds'), ('price_plus_nds', 'summ_nds'))
        }),
    )

    # fields = ['number', 'date', 'title', 'comment', 'eosdo',
    #                   'concurs', 'condition', 'closed', 'guarantee_letter', 'soprovojdenie', 'otvetstvenny',
    #                   'date_begin', 'date_end_plan', 'date_end_prognoz', 'date_end_fact', 'control_VP',
    #                   'client_name', 'great_client',
    #                   'great_department', 'general_client', 'status_contract', 'igk', 'price_no_nds',
    #                   'nds', 'summ_nds', 'price_plus_nds', 'num_ng', 'num_stage']
    help_texts = {
        'title': 'Some help text for my field',
        'control_price': 'Some help text for my field',
        'guarantee_letter': 'Some help text for my field',
    }

    # def has_change_permission(self, request, obj=None):
    #     if obj and request.user.has_perm('contract.change_contract') and request.user.has_perm(
    #             'contract.close_contract'):
    #         # пользователь имеет права изменения и закрытия договора
    #         return True
    #     return False


admin.site.register(Contract, ContractAdmin)


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract')
    list_editable = ('contract',)


class StageBeginListAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract_id', 'contract', 'ispolnitel', 'date_end_plan')
    list_display_links = ('id', 'contract')
    list_editable = ('ispolnitel', 'date_end_plan')
    list_filter = ('ispolnitel',)


admin.site.register(StageBeginList, StageBeginListAdmin)
admin.site.register(StageMiddleList)
admin.site.register(StageEndList)


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'number', 'date', 'ispolnitel', 'status', 'content', 'file'
    )
    list_display_links = ('id', 'number')
    readonly_fields = ('contract', 'last_change')
    list_editable = ()
    list_filter = ('status',)
    fieldsets = (
        ('', {
            'fields': (
                'contract', ('number', 'date'), 'ispolnitel', 'status',
                'content', 'file'
            )
        }),
        ('Изменения', {'fields': ('last_change',)}),
    )


@admin.register(AddAgreement)
class AddAgreementAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'number', 'date', 'comment', 'file')
    list_display_links = ('id', 'number')
    readonly_fields = ('contract', 'last_change')
    list_editable = ()
    fieldsets = (
        ('', {
            'fields': ('contract', ('number', 'date'), 'comment', 'file')
        }),
        ('Изменения', {'fields': ('last_change',)}),
    )


class TimeWorkAdmin(admin.ModelAdmin):
    list_display = ('member', 'contract', 'time', 'sum_work')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.values('member', 'contract').annotate(sum_work=Coalesce(Sum('time'), 0))
        return qs

    def sum_work(self, obj):
        return obj['sum_work']

    sum_work.short_description = 'Sum Work'


admin.site.register(TimeWork, TimeWorkAdmin)














# class UserAdmin(BaseUserAdmin):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.list_display += ('contract_close',)
#
#     def get_custom_permission(self, obj):
#         return obj.get_custom_permission_display()
#
#     get_custom_permission.short_description = 'Custom Permission'
#     get_custom_permission.admin_order_field = 'custom_permission'
#
# admin.site.unregister(Permission)
# admin.site.register(CustomPermission, UserAdmin)


# admin.site.register(Continent)
# admin.site.register(Country)
# admin.site.register(Location)

# admin.site.register(price_range)

# admin.site.register(Product)
# admin.site.register(Movie)
# admin.site.register(MyData)