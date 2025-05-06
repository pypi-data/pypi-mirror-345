from django.contrib import admin
from finance_mt940.actions import upload_mt940_file
from .models import OrderAccount
from .models import BankStatement


@admin.register(OrderAccount)
class OrderAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'iban', 'bic']
    list_filter = ['name', 'iban', 'bic']
    actions = [upload_mt940_file]


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_select_related = True
    date_hierarchy = 'entry_date'
    list_display = [
        'order_account',
        'amount',
        'currency',
        'applicant_name',
        'applicant_iban',
        'posting_text',
        'entry_date',
        ]
    list_filter = [
        'entry_date',
        'currency',
        'applicant_name',
        'posting_text',
        ]

    def has_change_permission(self, request, obj=None):
        return False
