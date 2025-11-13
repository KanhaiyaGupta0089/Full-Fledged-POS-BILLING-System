"""
Email templates and sending functions
"""
import re
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notification
from accounts.models import User
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


def send_email_notification(subject, message, recipient_email, user=None, metadata=None, html_message=None, attachments=None):
    """Send email notification"""
    try:
        if html_message:
            # Send HTML email
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.content_subtype = "html"
            
            # Attach files if provided
            if attachments:
                for attachment in attachments:
                    email.attach(*attachment)
            
            email.send()
        else:
            # Send plain text email
            if attachments:
                # If attachments are provided, use EmailMessage
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient_email],
                )
                for attachment in attachments:
                    email.attach(*attachment)
                email.send()
            else:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
        
        # Create notification record
        Notification.objects.create(
            user=user,
            notification_type='email',
            subject=subject,
            message=message,
            recipient_email=recipient_email,
            status='sent',
            metadata=metadata or {}
        )
        return True
    except Exception as e:
        # Create failed notification record
        try:
            Notification.objects.create(
                user=user,
                notification_type='email',
                subject=subject,
                message=message,
                recipient_email=recipient_email,
                status='failed',
                error_message=str(e),
                metadata=metadata or {}
            )
        except:
            pass
        return False


def send_invoice_email(invoice, recipient_email):
    """Send invoice email to customer"""
    subject = f"Invoice {invoice.invoice_number} - {settings.DEFAULT_FROM_EMAIL}"
    message = f"""
Dear Customer,

Thank you for your purchase!

Invoice Number: {invoice.invoice_number}
Date: {invoice.created_at.strftime('%Y-%m-%d %H:%M')}
Total Amount: ₹{invoice.total_amount}

Items:
{chr(10).join([f"- {item.product.name} x {item.quantity} = ₹{item.total}" for item in invoice.items.all()])}

Payment Status: {invoice.get_status_display()}
Paid Amount: ₹{invoice.paid_amount}
Balance: ₹{invoice.balance_amount}

Thank you for your business!
"""
    return send_email_notification(subject, message, recipient_email, metadata={'invoice_id': invoice.id})


def generate_low_stock_pdf(low_stock_products):
    """Generate PDF for low stock products"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Define color scheme
    purple_dark = colors.HexColor('#6B46C1')
    green_light = colors.HexColor('#10B981')
    light_grey = colors.HexColor('#F3F4F6')
    white = colors.white
    
    # Header
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=20,
        textColor=white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    header_data = [[Paragraph("Low Stock Products Alert", header_style)]]
    header_table = Table(header_data, colWidths=[7*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), purple_dark),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Date
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica',
        alignment=TA_CENTER
    )
    from django.utils import timezone
    date_text = Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y %I:%M %p')}", date_style)
    story.append(date_text)
    story.append(Spacer(1, 0.2*inch))
    
    # Products table - use Paragraph for SKU to handle long text properly
    sku_style = ParagraphStyle(
        'SKUStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        fontName='Helvetica',
        wordWrap='CJK'  # Enable word wrapping
    )
    
    products_data = [['#', 'Product Name', 'SKU', 'Current Stock', 'Min Stock', 'Status']]
    
    for idx, product in enumerate(low_stock_products, 1):
        stock_status = 'Critical' if product.current_stock == 0 else 'Low'
        # Use Paragraph for SKU to handle long strings properly
        sku_text = product.sku or 'N/A'
        
        # Clean product name - remove " - #XXXXXX" pattern if present
        product_name = re.sub(r'\s*-\s*#\d+$', '', product.name).strip()
        
        products_data.append([
            str(idx),
            product_name,  # Use cleaned product name without -# pattern
            Paragraph(sku_text, sku_style),  # Use Paragraph for proper text wrapping
            str(product.current_stock),
            str(product.min_stock_level),
            stock_status
        ])
    
    # Adjusted column widths - increased Product Name column width and Current Stock column
    products_table = Table(products_data, colWidths=[0.4*inch, 2.1*inch, 2*inch, 1*inch, 0.9*inch, 0.8*inch])
    products_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), green_light),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # # column
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),   # Product Name
        ('ALIGN', (2, 0), (2, 0), 'LEFT'),   # SKU
        ('ALIGN', (3, 0), (3, 0), 'CENTER'), # Current Stock
        ('ALIGN', (4, 0), (4, 0), 'CENTER'), # Min Stock
        ('ALIGN', (5, 0), (5, 0), 'CENTER'), # Status
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # # column
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Product Name
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # SKU
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Current Stock
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Min Stock
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Status
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),   # Top align to handle wrapped text
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, light_grey]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(products_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, 
                                  fontSize=8, textColor=colors.grey, spaceBefore=20)
    footer = Paragraph(
        "Please reorder these products soon to avoid stockouts.<br/>This is an automated low stock alert.",
        footer_style
    )
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def send_daily_summary_email(user, summary_data):
    """Send daily business summary email with HTML tables"""
    from datetime import datetime
    
    subject = f"Daily Business Summary - {summary_data.get('date', '')}"
    
    # Prepare attachments (low stock PDF if available)
    attachments = []
    low_stock_products = summary_data.get('low_stock_products')
    if low_stock_products and low_stock_products.exists():
        try:
            pdf_buffer = generate_low_stock_pdf(low_stock_products)
            attachments.append((
                'low_stock_products.pdf',
                pdf_buffer.getvalue(),
                'application/pdf'
            ))
        except Exception as e:
            print(f"Error generating low stock PDF: {str(e)}")
            # Continue without PDF if generation fails
    
    # Format date for display
    try:
        date_obj = datetime.fromisoformat(summary_data.get('date', ''))
        formatted_date = date_obj.strftime('%B %d, %Y')
    except:
        formatted_date = summary_data.get('date', '')
    
    # Build top products table rows
    top_products = summary_data.get('top_products', [])
    top_products_rows = ''
    if top_products:
        for idx, product in enumerate(top_products[:5], 1):
            product_name = product.get('name', 'N/A')
            quantity = product.get('quantity', 0)
            top_products_rows += f"""
            <tr>
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{idx}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{product_name}</td>
                <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">{quantity}</td>
            </tr>
            """
    else:
        top_products_rows = """
            <tr>
                <td colspan="3" style="padding: 8px; text-align: center; border: 1px solid #ddd;">No products sold today</td>
            </tr>
        """
    
    # HTML email template
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #6B46C1;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 0 0 5px 5px;
            }}
            .summary-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
            }}
            .summary-table th {{
                background-color: #10B981;
                color: white;
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            .summary-table td {{
                padding: 10px;
                border: 1px solid #ddd;
            }}
            .summary-table tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            .products-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
            }}
            .products-table th {{
                background-color: #6B46C1;
                color: white;
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            .products-table td {{
                padding: 8px;
                border: 1px solid #ddd;
            }}
            .products-table tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            .highlight {{
                font-weight: bold;
                color: #6B46C1;
            }}
            .footer {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Daily Business Summary</h1>
                <p>Date: {formatted_date}</p>
            </div>
            <div class="content">
                <h2>Business Overview</h2>
                <table class="summary-table">
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Total Sales</td>
                        <td class="highlight">₹{summary_data.get('total_sales', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td>Total Invoices</td>
                        <td class="highlight">{summary_data.get('total_invoices', 0)}</td>
                    </tr>
                    <tr>
                        <td>Total Profit</td>
                        <td class="highlight">₹{summary_data.get('total_profit', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td>Profit Margin</td>
                        <td class="highlight">{summary_data.get('profit_margin', 0)}%</td>
                    </tr>
                    <tr>
                        <td>Low Stock Alerts</td>
                        <td class="highlight">{summary_data.get('low_stock_count', 0)} products</td>
                    </tr>
                </table>
                
                <h2>Top Selling Products</h2>
                <table class="products-table">
                    <thead>
                        <tr>
                            <th style="text-align: center; width: 50px;">#</th>
                            <th>Product Name</th>
                            <th style="text-align: right;">Quantity Sold</th>
                        </tr>
                    </thead>
                    <tbody>
                        {top_products_rows}
                    </tbody>
                </table>
                
                <div class="footer">
                    <p>This is an automated daily business summary report.</p>
                    <p>Thank you for using POS Billing System!</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text fallback
    message = f"""
Daily Business Summary

Date: {formatted_date}
Total Sales: ₹{summary_data.get('total_sales', 0):,.2f}
Total Invoices: {summary_data.get('total_invoices', 0)}
Total Profit: ₹{summary_data.get('total_profit', 0):,.2f}
Profit Margin: {summary_data.get('profit_margin', 0)}%

Top Selling Products:
{chr(10).join([f"{idx}. {p.get('name', 'N/A')}: {p.get('quantity', 0)} units" for idx, p in enumerate(summary_data.get('top_products', [])[:5], 1)])}

Low Stock Alerts: {summary_data.get('low_stock_count', 0)} products

Thank you!
"""
    
    return send_email_notification(
        subject=subject, 
        message=message, 
        recipient_email=user.email, 
        user=user, 
        metadata={'summary_date': summary_data.get('date')},
        html_message=html_message,
        attachments=attachments if attachments else None
    )


def send_low_stock_alert(product, user=None):
    """Send low stock alert"""
    subject = f"Low Stock Alert - {product.name}"
    message = f"""
Low Stock Alert

Product: {product.name} ({product.sku})
Current Stock: {product.current_stock}
Minimum Stock Level: {product.min_stock_level}

Please reorder soon!
"""
    # Send to admin/manager
    admins = User.objects.filter(role__in=['admin', 'manager', 'owner'])
    for admin in admins:
        send_email_notification(subject, message, admin.email, user=admin, metadata={'product_id': product.id})

