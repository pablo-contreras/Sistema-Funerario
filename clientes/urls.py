from django.urls import path

from . import views

app_name = "clientes"

urlpatterns = [
    path("", views.client_list, name="list"),
    path("clientes/nuevo/", views.client_create, name="create"),
    path("clientes/<int:pk>/", views.client_detail, name="detail"),
    path("clientes/<int:pk>/editar/", views.client_update, name="update"),
    path("clientes/<int:pk>/eliminar/", views.client_delete, name="delete"),
    path("clientes/<int:pk>/pagos/nuevo/", views.payment_create, name="payment_create"),
    path("pagos/<int:pk>/eliminar/", views.payment_delete, name="payment_delete"),
    path("clientes/<int:pk>/documentos/subir/", views.document_upload, name="document_upload"),
    path("documentos/<int:pk>/descargar/", views.document_download, name="document_download"),
    path("documentos/<int:pk>/eliminar/", views.document_delete, name="document_delete"),
    path("clientes/<int:pk>/contrato/", views.contract_print, name="contract_print"),
    path("clientes/<int:pk>/contrato.pdf", views.contract_pdf, name="contract_pdf"),
]
