import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from clientes.models import Client, ClientDocument, Payment
from clientes.validators import normalize_rut


TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class FuneralSystemTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = get_user_model().objects.create_user("operador", password="Clave-Segura-2026")
        self.client.force_login(self.user)

    def test_client_only_requires_name_and_rut(self):
        response = self.client.post(
            reverse("clientes:create"),
            {"name": "María Soto", "rut": "12.345.678-5", "vat_rate": "19"},
        )
        self.assertEqual(response.status_code, 302)
        record = Client.objects.get()
        self.assertEqual(record.rut, "12345678-5")
        self.assertTrue(record.folio.startswith("FUN-"))

    def test_searches_by_name_and_rut(self):
        Client.objects.create(name="Juan Pérez", rut="11.111.111-1")
        by_name = self.client.get(reverse("clientes:list"), {"q": "Juan"})
        by_rut = self.client.get(reverse("clientes:list"), {"q": "11.111.111-1"})
        arbitrary = self.client.get(reverse("clientes:list"), {"q": "kk"})
        self.assertContains(by_name, "Juan Pérez")
        self.assertContains(by_rut, "Juan Pérez")
        self.assertEqual(arbitrary.status_code, 200)

    def test_payments_update_balance(self):
        record = Client.objects.create(name="Ana Díaz", rut="12.345.678-5", service_net=100000)
        Payment.objects.create(client=record, amount=Decimal("30000"))
        self.assertEqual(record.service_total, Decimal("119000"))
        self.assertEqual(record.paid_total, Decimal("30000"))
        self.assertEqual(record.balance, Decimal("89000"))

    def test_document_is_stored_in_client_folder(self):
        record = Client.objects.create(name="Pedro Lagos", rut="12.345.678-5")
        upload = SimpleUploadedFile("contrato.pdf", b"archivo de prueba", content_type="application/pdf")
        document = ClientDocument.objects.create(client=record, file=upload, original_name="contrato.pdf")
        self.assertIn(record.document_folder, document.file.name)
        self.assertTrue(document.file.storage.exists(document.file.name))

    def test_rut_normalization(self):
        self.assertEqual(normalize_rut("12.345.678-5"), "12345678-5")

    def test_contract_pdf_download(self):
        record = Client.objects.create(name="Laura Silva", rut="12.345.678-5", service_net=100000)
        response = self.client.get(reverse("clientes:contract_pdf", args=[record.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
