from django.contrib import admin
from .models import Croprate, Invoice
from import_export.admin import ImportExportModelAdmin

# Register your models here.
@admin.register(Croprate)
class CroprateModelAdmin(ImportExportModelAdmin):
    list_display = ('id', 'tomato_rate', 'bellpepper_rate', 'cucumber_rate', 
                    'abernero_rate')


@admin.register(Invoice)
class InvoiceModelAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'address', 'phone_no', 'email', 'tomatoes', 'bell_pepper', 'cucumber',
                    'abernero', 'total_price', 'invoice_number','created_at')
