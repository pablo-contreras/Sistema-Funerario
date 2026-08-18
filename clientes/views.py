import os
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ClientForm, DocumentForm, PaymentForm
from .models import Client, ClientDocument, Payment
from .validators import normalize_rut


def contract_context(client, request=None, pdf_mode=False):
    running_balance = client.service_total
    payments_with_balance = []
    for payment in client.payments.all():
        running_balance -= payment.amount
        payments_with_balance.append((payment, running_balance))
    return {
        "client": client,
        "payments_with_balance": payments_with_balance,
        "pdf_mode": pdf_mode,
        "request": request,
        "logo_uri": (settings.BASE_DIR / "static" / "img" / "logo.png").as_uri(),
    }


@login_required
def client_list(request):
    query = request.GET.get("q", "").strip()
    clients = Client.objects.annotate(paid_amount=Sum("payments__amount"))
    if query:
        search_filter = (
            Q(name__icontains=query)
            | Q(rut__icontains=query)
            | Q(deceased_name__icontains=query)
            | Q(folio__icontains=query)
        )
        normalized_query = normalize_rut(query)
        if normalized_query:
            search_filter |= Q(rut__icontains=normalized_query)
        clients = clients.filter(search_filter)
    return render(
        request,
        "clientes/client_list.html",
        {"clients": clients[:100], "query": query, "total_clients": Client.objects.count()},
    )


@login_required
def client_create(request):
    form = ClientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        client = form.save(commit=False)
        client.created_by = request.user
        client.save()
        messages.success(request, "La ficha del cliente fue creada.")
        return redirect("clientes:detail", pk=client.pk)
    return render(request, "clientes/client_form.html", {"form": form, "title": "Nueva ficha"})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La ficha fue actualizada.")
        return redirect("clientes:detail", pk=client.pk)
    return render(
        request,
        "clientes/client_form.html",
        {"form": form, "title": "Editar ficha", "client": client},
    )


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client.objects.prefetch_related("payments", "documents"), pk=pk)
    return render(
        request,
        "clientes/client_detail.html",
        {"client": client, "payment_form": PaymentForm(), "document_form": DocumentForm()},
    )


@login_required
@require_POST
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    name = client.name
    client.delete()
    messages.success(request, f"La ficha de {name} fue eliminada.")
    return redirect("clientes:list")


@login_required
@require_POST
def payment_create(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = PaymentForm(request.POST)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.client = client
        payment.save()
        messages.success(request, "Pago registrado correctamente.")
    else:
        messages.error(request, "Revise los datos del pago.")
    return redirect(f"{reverse('clientes:detail', args=[client.pk])}#pagos")


@login_required
@require_POST
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    client_pk = payment.client_id
    payment.delete()
    messages.success(request, "Pago eliminado.")
    return redirect(f"{reverse('clientes:detail', args=[client_pk])}#pagos")


@login_required
@require_POST
def document_upload(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.client = client
        document.uploaded_by = request.user
        document.original_name = Path(document.file.name).name
        document.save()
        messages.success(request, "Archivo guardado en la carpeta del cliente.")
    else:
        messages.error(request, "No fue posible subir el archivo. Revise el tipo y tamaño.")
    return redirect(f"{reverse('clientes:detail', args=[client.pk])}#archivos")


@login_required
def document_download(request, pk):
    document = get_object_or_404(ClientDocument, pk=pk)
    try:
        return FileResponse(document.file.open("rb"), as_attachment=True, filename=document.original_name)
    except FileNotFoundError as exc:
        raise Http404("El archivo ya no existe en el disco.") from exc


@login_required
@require_POST
def document_delete(request, pk):
    document = get_object_or_404(ClientDocument, pk=pk)
    client_pk = document.client_id
    document.delete()
    messages.success(request, "Archivo eliminado.")
    return redirect(f"{reverse('clientes:detail', args=[client_pk])}#archivos")


@login_required
def contract_print(request, pk):
    client = get_object_or_404(Client.objects.prefetch_related("payments"), pk=pk)
    return render(request, "clientes/contract_print.html", contract_context(client, request=request))


@login_required
def contract_pdf(request, pk):
    client = get_object_or_404(Client.objects.prefetch_related("payments"), pk=pk)
    context = contract_context(client, request=request, pdf_mode=True)
    html = render_to_string("clientes/contract_print.html", context)
    try:
        if os.name == "nt":
            raise OSError("Use ReportLab on Windows")
        from weasyprint import HTML

        pdf = HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf()
    except (ImportError, OSError):
        from .pdf_fallback import generate_contract_pdf

        pdf = generate_contract_pdf(client, context["payments_with_balance"])
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="contrato-{client.folio}.pdf"'
    return response
