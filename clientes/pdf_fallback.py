from io import BytesIO
from html import escape

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def money(value):
    return f"${value or 0:,.0f}".replace(",", ".")


def value(value):
    return escape(str(value)) if value not in (None, "") else "________________"


def section(title, rows, styles):
    content = [Paragraph(title.upper(), styles["section"])]
    data = []
    for left_label, left_value, right_label, right_value in rows:
        data.append(
            [
                Paragraph(f"<font size='7' color='#64748b'>{left_label}</font><br/><b>{value(left_value)}</b>", styles["cell"]),
                Paragraph(f"<font size='7' color='#64748b'>{right_label}</font><br/><b>{value(right_value)}</b>", styles["cell"]),
            ]
        )
    table = Table(data, colWidths=[91 * mm, 91 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#aeb8c5")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d8dee8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fcfdfc")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    content.extend([table, Spacer(1, 3 * mm)])
    return content


def header(title, client, styles):
    logo_path = settings.BASE_DIR / "static" / "img" / "logo.png"
    logo = Image(str(logo_path), width=14 * mm, height=14 * mm)
    title_block = Paragraph(f"<b>{title}</b><br/><font size='8'>Servicios funerarios</font>", styles["header"])
    date_text = client.contract_date.strftime("%d/%m/%Y") if client.contract_date else "—"
    facts = Paragraph(
        f"<b>Folio:</b> {client.folio}<br/><b>Fecha:</b> {date_text}",
        styles["facts"],
    )
    table = Table([[logo, title_block, facts]], colWidths=[18 * mm, 117 * mm, 47 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#486348")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return [table, Spacer(1, 5 * mm)]


def generate_contract_pdf(client, payments_with_balance):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=10 * mm, rightMargin=10 * mm, topMargin=8 * mm, bottomMargin=8 * mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="header", parent=styles["Normal"], textColor=colors.white, fontSize=15, leading=18))
    styles.add(ParagraphStyle(name="facts", parent=styles["Normal"], textColor=colors.white, alignment=TA_RIGHT, fontSize=8, leading=12))
    styles.add(ParagraphStyle(name="section", parent=styles["Heading2"], textColor=colors.HexColor("#486348"), fontSize=10, spaceAfter=4))
    styles.add(ParagraphStyle(name="cell", parent=styles["Normal"], fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="small", parent=styles["Normal"], fontSize=8, leading=11))
    styles.add(ParagraphStyle(name="center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8))

    story = header("Contrato de Servicios Funerarios", client, styles)
    story += section(
        "Datos del contratante",
        [
            ("CONTRATANTE", client.name, "RUT", client.rut),
            ("DOMICILIO", client.address, "TELÉFONO", client.phone),
            ("CORREO", client.email, "PARENTESCO", client.relationship),
        ],
        styles,
    )
    story += section(
        "Datos del fallecido",
        [
            ("FALLECIDO", client.deceased_name, "RUT", client.deceased_rut),
            ("DOMICILIO", client.deceased_address, "EDAD", client.age),
            ("LUGAR NACIMIENTO", client.birth_place, "ESTADO CIVIL", client.marital_status),
            ("FECHA FALLECIMIENTO", client.death_date, "HORA", client.death_time),
            ("LUGAR FALLECIMIENTO", client.death_place, "INSCRIPCIÓN", client.registration_place),
            ("PADRES", client.parents, "PREVISIÓN", client.insurance),
        ],
        styles,
    )
    story += section(
        "Servicio y ceremonia",
        [
            ("TIPO DE URNA", client.urn_type, "TRASLADO", client.cemetery_transfer),
            ("LUGAR VELACIÓN", client.wake_place, "IGLESIA", client.church),
            ("FECHA MISA", client.mass_date, "HORA", client.mass_time),
            ("AUTOMÓVIL", client.automobile, "MICROBÚS", client.minibus),
        ],
        styles,
    )
    totals = Table(
        [
            ["Concepto", "Detalle", "Valor"],
            ["Servicio funerario", client.service_description, money(client.service_net)],
            [f"IVA {client.vat_rate:.0f}%", "", money(client.vat_amount)],
            ["TOTAL", "", money(client.service_total)],
        ],
        colWidths=[43 * mm, 102 * mm, 37 * mm],
    )
    totals.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#aeb8c5")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf1ea")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f3f5f7")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.extend(
        [
            totals,
            Spacer(1, 4 * mm),
            Paragraph("<b>Texto legal:</b> El contratante se hace responsable de la cancelación total de la deuda adquirida por el servicio funerario.", styles["small"]),
            Spacer(1, 15 * mm),
            Table([[f"______________________________<br/>{client.seller_name or 'VENDEDOR'}", f"______________________________<br/>{client.name}"]], colWidths=[91 * mm, 91 * mm], style=[("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTSIZE", (0, 0), (-1, -1), 8)]),
            PageBreak(),
        ]
    )

    story += header("Entrega de Documentos y Registro de Pagos", client, styles)
    story += section(
        "Entrega de documentos",
        [
            ("RECEPTOR", client.documents_recipient, "PARENTESCO", client.documents_relationship),
            ("FECHA", client.documents_date, "DETALLE", client.documents_detail),
        ],
        styles,
    )
    payment_data = [["Fecha abono", "Valor", "Saldo", "N° recibo"]]
    for payment, balance in payments_with_balance:
        payment_data.append([payment.payment_date.strftime("%d/%m/%Y"), money(payment.amount), money(balance), payment.receipt_number])
    if len(payment_data) == 1:
        payment_data.extend([["", "", "", ""] for _ in range(4)])
    payment_table = Table(payment_data, colWidths=[43 * mm, 45 * mm, 47 * mm, 47 * mm], rowHeights=9 * mm)
    payment_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#aeb8c5")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf1ea")), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("ALIGN", (1, 1), (2, -1), "RIGHT"), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
    story.extend(
        [
            payment_table,
            Spacer(1, 5 * mm),
            Paragraph(f"<b>Total deuda:</b> {money(client.service_total)} &nbsp;&nbsp; <b>Pagado:</b> {money(client.paid_total)} &nbsp;&nbsp; <b>Saldo:</b> {money(client.balance)}", styles["small"]),
            Spacer(1, 6 * mm),
            Paragraph(f"<b>Observaciones:</b><br/>{value(client.observations)}", styles["small"]),
        ]
    )
    doc.build(story)
    return buffer.getvalue()
