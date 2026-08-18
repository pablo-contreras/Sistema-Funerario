from django import forms

from .models import Client, ClientDocument, Payment
from .validators import normalize_rut


class DateInput(forms.DateInput):
    input_type = "date"


class TimeInput(forms.TimeInput):
    input_type = "time"


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ["folio", "document_folder", "created_by", "created_at", "updated_at"]
        widgets = {
            "birth_date": DateInput(),
            "death_date": DateInput(),
            "death_time": TimeInput(),
            "mass_date": DateInput(),
            "mass_time": TimeInput(),
            "contract_date": DateInput(),
            "documents_date": DateInput(),
            "service_description": forms.Textarea(attrs={"rows": 2}),
            "documents_detail": forms.Textarea(attrs={"rows": 2}),
            "observations": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["name"].widget.attrs.update({"autofocus": True, "placeholder": "Nombre completo"})
        self.fields["rut"].widget.attrs.update({"placeholder": "12.345.678-5"})

    def clean_rut(self):
        return normalize_rut(self.cleaned_data["rut"])


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["payment_date", "amount", "receipt_number", "notes"]
        widgets = {"payment_date": DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class DocumentForm(forms.ModelForm):
    class Meta:
        model = ClientDocument
        fields = ["category", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["file"].widget.attrs["accept"] = ".pdf,.jpg,.jpeg,.png,.webp,.doc,.docx,.xls,.xlsx"

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        if uploaded.size > 20 * 1024 * 1024:
            raise forms.ValidationError("El archivo no puede superar 20 MB.")
        return uploaded
