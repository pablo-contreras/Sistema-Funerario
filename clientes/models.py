from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone

from .validators import normalize_rut, validate_rut


def client_document_path(instance, filename):
    folder = instance.client.document_folder or f"cliente-{instance.client_id}"
    return str(Path("clientes") / folder / filename)


class Client(models.Model):
    name = models.CharField("Nombre del contratante", max_length=200)
    rut = models.CharField("RUT", max_length=20, unique=True, validators=[validate_rut])
    folio = models.CharField(max_length=30, unique=True, blank=True)
    address = models.CharField("Domicilio", max_length=250, blank=True)
    phone = models.CharField("Teléfono", max_length=40, blank=True)
    occupation = models.CharField("Ocupación", max_length=120, blank=True)
    email = models.EmailField("Correo electrónico", blank=True)
    relationship = models.CharField("Parentesco", max_length=120, blank=True)

    deceased_name = models.CharField("Nombre del fallecido", max_length=200, blank=True)
    deceased_address = models.CharField("Domicilio del fallecido", max_length=250, blank=True)
    deceased_rut = models.CharField("RUT del fallecido", max_length=20, blank=True)
    birth_place = models.CharField("Lugar de nacimiento", max_length=150, blank=True)
    age = models.PositiveSmallIntegerField("Edad", null=True, blank=True)
    marital_status = models.CharField("Estado civil", max_length=80, blank=True)
    education = models.CharField("Estudios", max_length=120, blank=True)
    insurance = models.CharField("Previsión", max_length=120, blank=True)
    birth_date = models.DateField("Fecha de nacimiento", null=True, blank=True)
    death_date = models.DateField("Fecha de fallecimiento", null=True, blank=True)
    death_time = models.TimeField("Hora de fallecimiento", null=True, blank=True)
    death_place = models.CharField("Lugar de fallecimiento", max_length=250, blank=True)
    registration_place = models.CharField("Lugar de inscripción", max_length=250, blank=True)
    parents = models.CharField("Nombre de los padres", max_length=300, blank=True)

    urn_type = models.CharField("Tipo de urna", max_length=150, blank=True)
    cemetery_transfer = models.CharField("Traslado al cementerio", max_length=200, blank=True)
    wake_place = models.CharField("Lugar de velación", max_length=250, blank=True)
    mass_date = models.DateField("Fecha de misa", null=True, blank=True)
    mass_time = models.TimeField("Hora de misa", null=True, blank=True)
    church = models.CharField("Iglesia", max_length=200, blank=True)
    automobile = models.CharField("Automóvil", max_length=150, blank=True)
    automobile_paid_by = models.CharField("Automóvil pagado por", max_length=150, blank=True)
    minibus = models.CharField("Microbús", max_length=150, blank=True)
    minibus_paid_by = models.CharField("Microbús pagado por", max_length=150, blank=True)

    service_description = models.TextField("Detalle del servicio", blank=True)
    service_net = models.DecimalField(
        "Valor neto del servicio",
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    vat_rate = models.DecimalField("IVA (%)", max_digits=5, decimal_places=2, default=Decimal("19"), blank=True)
    seller_name = models.CharField("Vendedor", max_length=160, blank=True)
    contract_place = models.CharField("Lugar del contrato", max_length=100, default="Limache", blank=True)
    contract_date = models.DateField("Fecha del contrato", default=timezone.localdate, null=True, blank=True)

    documents_recipient = models.CharField("Receptor de documentos", max_length=200, blank=True)
    documents_relationship = models.CharField("Parentesco del receptor", max_length=100, blank=True)
    documents_date = models.DateField("Fecha de entrega", null=True, blank=True)
    documents_detail = models.TextField("Documentos entregados", blank=True)
    observations = models.TextField("Observaciones", blank=True)

    document_folder = models.CharField(max_length=255, blank=True, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_clients",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return f"{self.name} ({self.rut})"

    def save(self, *args, **kwargs):
        self.rut = normalize_rut(self.rut)
        super().save(*args, **kwargs)
        update_fields = []
        if not self.folio:
            self.folio = f"FUN-{self.created_at:%Y}-{self.pk:05d}"
            update_fields.append("folio")
        if not self.document_folder:
            base = slugify(self.name)[:80] or "cliente"
            rut_part = self.rut.replace(".", "").replace("-", "_")
            self.document_folder = f"{base}-{rut_part}"
            update_fields.append("document_folder")
        if update_fields:
            super().save(update_fields=update_fields)

    @property
    def vat_amount(self):
        if self.service_net is None:
            return None
        return (self.service_net * self.vat_rate / Decimal("100")).quantize(Decimal("1"))

    @property
    def service_total(self):
        if self.service_net is None:
            return Decimal("0")
        return self.service_net + (self.vat_amount or Decimal("0"))

    @property
    def paid_total(self):
        if hasattr(self, "paid_amount"):
            return self.paid_amount or Decimal("0")
        return self.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    @property
    def balance(self):
        return self.service_total - self.paid_total


class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateField("Fecha del abono", default=timezone.localdate)
    amount = models.DecimalField(
        "Valor",
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("1"))],
    )
    receipt_number = models.CharField("N° de recibo", max_length=80, blank=True)
    notes = models.CharField("Detalle", max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["payment_date", "created_at"]
        verbose_name = "pago"
        verbose_name_plural = "pagos"

    def __str__(self):
        return f"{self.client.name}: ${self.amount}"


class ClientDocument(models.Model):
    CATEGORY_CHOICES = [
        ("contrato", "Contrato físico"),
        ("certificado", "Certificado"),
        ("comprobante", "Comprobante"),
        ("otro", "Otro"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="documents")
    category = models.CharField("Tipo", max_length=30, choices=CATEGORY_CHOICES, default="otro")
    file = models.FileField(
        "Archivo",
        upload_to=client_document_path,
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png", "webp", "doc", "docx", "xls", "xlsx"])],
    )
    original_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "documento"
        verbose_name_plural = "documentos"

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = Path(self.file.name).name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_name or Path(self.file.name).name


@receiver(post_delete, sender=ClientDocument)
def delete_document_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
