"""
Invoice PDF Generator - Professional Invoice Template
Based on standard professional invoice design
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


def format_currency(amount):
    """Format currency without rupee symbol to avoid encoding issues"""
    return f"Rs. {amount:,.2f}"


def generate_invoice_pdf(invoice):
    """Generate professional PDF invoice matching standard template design"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Define color scheme matching the template
    purple_dark = colors.HexColor('#6B46C1')  # Dark purple
    green_light = colors.HexColor('#10B981')  # Light green
    green_dark = colors.HexColor('#059669')  # Darker green
    light_grey = colors.HexColor('#F3F4F6')  # Light grey for alternating rows
    white = colors.white
    
    # Create custom styles
    company_name_style = ParagraphStyle(
        'CompanyName',
        parent=styles['Normal'],
        fontSize=16,
        textColor=white,
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    
    company_info_style = ParagraphStyle(
        'CompanyInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=white,
        fontName='Helvetica',
        spaceAfter=2
    )
    
    invoice_title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontSize=36,
        textColor=green_light,
        fontName='Helvetica-Bold'
    )
    
    section_label_style = ParagraphStyle(
        'SectionLabel',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    body_text_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    # ========== HEADER SECTION - Purple Banner ==========
    # Company info (left side of purple banner)
    company_info_data = [
        [Paragraph("POS Billing System", company_name_style)],
        [Paragraph("Email: billing@possystem.com", company_info_style)],
        [Paragraph("Phone: +91-1234567890", company_info_style)],
    ]
    
    company_table = Table(company_info_data, colWidths=[4*inch])
    company_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    # Invoice title (right side of purple banner)
    invoice_title_table = Table([[Paragraph("INVOICE", invoice_title_style)]], colWidths=[2.5*inch])
    invoice_title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    # Combine header
    header_data = [
        [company_table, invoice_title_table]
    ]
    
    header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), purple_dark),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (0, -1), 20),
        ('RIGHTPADDING', (1, 0), (1, -1), 20),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ========== BILL TO & INVOICE DETAILS SECTION ==========
    customer_name = invoice.customer.name if invoice.customer else invoice.customer_name or 'Walk-in Customer'
    customer_phone = invoice.customer_phone or (invoice.customer.phone if invoice.customer else 'N/A')
    customer_email = invoice.customer_email or (invoice.customer.email if invoice.customer else 'N/A')
    customer_address = invoice.customer.address if invoice.customer else 'N/A'
    
    # Calculate due date (5 days from invoice date)
    from datetime import timedelta
    due_date = invoice.created_at + timedelta(days=5)
    
    # Create aligned Bill To and Invoice Details with same number of rows
    bill_to_data = [
        [Paragraph("Bill To", section_label_style), ''],
        [Paragraph("Name :", label_style), Paragraph(customer_name, value_style)],
        [Paragraph("Address :", label_style), Paragraph(customer_address, value_style)],
        [Paragraph("Phone :", label_style), Paragraph(customer_phone, value_style)],
        [Paragraph("Email :", label_style), Paragraph(customer_email, value_style)]
    ]
    
    invoice_details_data = [
        [Paragraph("Invoice Details", section_label_style), ''],
        [Paragraph("Invoice No :", label_style), Paragraph(invoice.invoice_number, value_style)],
        [Paragraph("Invoice Date :", label_style), Paragraph(invoice.created_at.strftime('%b %d, %Y'), value_style)],
        [Paragraph("Due Date :", label_style), Paragraph(due_date.strftime('%b %d, %Y'), value_style)],
        [Paragraph("Status :", label_style), Paragraph(invoice.get_status_display(), value_style)],
    ]
    
    # Combine Bill To and Invoice Details side by side
    # Increased column width for Invoice Details label column to prevent "Invoice Details" from wrapping
    info_data = [
        [
            Table(bill_to_data, colWidths=[1.2*inch, 2*inch]),
            Table(invoice_details_data, colWidths=[1.5*inch, 1.7*inch])
        ]
    ]
    
    info_table = Table(info_data, colWidths=[3.5*inch, 3.2*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ========== LINE ITEMS TABLE ==========
    items_data = [['Sl.', 'Description', 'Qty', 'Rate', 'Amount']]
    
    sl_no = 1
    for item in invoice.items.all():
        items_data.append([
            str(sl_no),
            item.product.name,
            str(item.quantity),
            format_currency(item.unit_price),
            format_currency(item.total)
        ])
        sl_no += 1
    
    items_table = Table(items_data, colWidths=[0.4*inch, 3*inch, 0.6*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        # Header row - Light green background
        ('BACKGROUND', (0, 0), (-1, 0), green_light),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (2, 0), (-1, 0), 'CENTER'),
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, light_grey]),
        # Borders
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ========== PAYMENT MODE & SUMMARY SECTION ==========
    # Payment Mode (left side)
    payment_mode_data = [
        [Paragraph("Payment Mode :", label_style), Paragraph(invoice.get_payment_method_display(), value_style)]
    ]
    
    payment_mode_table = Table(payment_mode_data, colWidths=[1.5*inch, 1.5*inch])
    payment_mode_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    # Summary (right side)
    summary_data = [
        ['Subtotal', format_currency(invoice.subtotal)],
        ['Discount', format_currency(invoice.discount_amount)],
        ['Tax', format_currency(invoice.tax_amount)],
        ['Total', format_currency(invoice.total_amount)],
        [f'Paid ({invoice.created_at.strftime("%b %d, %Y")})', format_currency(invoice.paid_amount)],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 1.8*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Balance Due - Special rounded bar style
    balance_due_data = [
        ['Balance Due', format_currency(invoice.balance_amount)]
    ]
    
    balance_due_table = Table(balance_due_data, colWidths=[2*inch, 1.8*inch])
    balance_due_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, 0), white),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.black),
        ('BACKGROUND', (0, 0), (0, 0), purple_dark),
        ('BACKGROUND', (1, 0), (1, 0), green_light),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    # Combine Summary and Balance Due
    summary_combined_data = [
        [summary_table],
        [balance_due_table]
    ]
    
    summary_combined_table = Table(summary_combined_data, colWidths=[3.8*inch])
    summary_combined_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    # Combine Payment Mode and Summary side by side
    payment_summary_data = [
        [payment_mode_table, summary_combined_table]
    ]
    
    payment_summary_table = Table(payment_summary_data, colWidths=[3.2*inch, 3.8*inch])
    payment_summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(payment_summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ========== FOOTER ==========
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, 
                                  fontSize=8, textColor=colors.grey, spaceBefore=20)
    footer = Paragraph(
        "Thank you for your business!<br/>This is a computer-generated invoice.",
        footer_style
    )
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
