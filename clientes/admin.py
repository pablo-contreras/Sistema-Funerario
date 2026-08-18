from django.contrib import admin

from .models import Client, ClientDocument, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class DocumentInline(admin.TabularInline):
    model = ClientDocument
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("folio", "name", "rut", "phone", "created_at")
    search_fields = ("name", "rut", "deceased_name")
    readonly_fields = ("folio", "document_folder", "created_at", "updated_at")
    inlines = [PaymentInline, DocumentInline]


admin.site.register(Payment)
admin.site.register(ClientDocument)
