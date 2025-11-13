"""
Product Label Generator - Printable QR Codes and Barcodes
Generates printable labels with QR codes, barcodes, and product information
"""
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from io import BytesIO
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image as PILImage
import io


def generate_qr_code_image(data, size=60):
    """Generate QR code image from data (optimized for labels)"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Lower error correction for smaller size
        box_size=3,  # Smaller box size for faster generation
        border=1,  # Smaller border
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    # Use LANCZOS resampling if available, otherwise use default
    try:
        img = img.resize((size, size), PILImage.Resampling.LANCZOS)  # Use LANCZOS for better quality at small size
    except AttributeError:
        # Fallback for older PIL versions
        img = img.resize((size, size), PILImage.LANCZOS)
    
    # Convert PIL Image to BytesIO with optimization
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG', optimize=True)  # Optimize PNG
    img_buffer.seek(0)
    return img_buffer


def generate_barcode_image(data, width=120, height=25):
    """Generate barcode image from data (optimized for labels)"""
    # Use Code128 barcode format
    code128 = Code128(data, writer=ImageWriter())
    
    # Generate barcode image with optimized settings
    img_buffer = BytesIO()
    code128.write(img_buffer, options={
        'module_width': 0.3,  # Smaller module width for faster generation
        'module_height': height,
        'quiet_zone': 1,  # Smaller quiet zone
        'font_size': 8,  # Smaller font
        'text_distance': 1,
        'center_text': True,
        'write_text': True,  # Include text below barcode
    })
    img_buffer.seek(0)
    return img_buffer


def generate_labels_pdf(products, labels_per_page=6, label_width=3.5*inch, label_height=2*inch):
    """Generate printable labels PDF with QR codes and barcodes
    
    Args:
        products: QuerySet or list of Product objects
        labels_per_page: Number of labels per page (default: 6 for 2x3 grid)
        label_width: Width of each label
        label_height: Height of each label
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Create custom styles
    product_name_style = ParagraphStyle(
        'ProductName',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica',
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=2
    )
    
    sku_style = ParagraphStyle(
        'SKU',
        parent=styles['Normal'],
        fontSize=7,
        fontName='Helvetica',
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=2
    )
    
    # Process products in batches - arrange in grid (2 columns, 3 rows per page)
    products_list = list(products)
    total_products = len(products_list)
    cols_per_page = 2  # 2 columns
    rows_per_page = labels_per_page // cols_per_page  # Calculate rows
    
    # Calculate label dimensions based on page size
    page_width = letter[0] - (0.5*inch * 2)  # Subtract margins
    page_height = letter[1] - (0.5*inch * 2)
    label_width = (page_width - (0.1*inch * (cols_per_page - 1))) / cols_per_page
    label_height = (page_height - (0.1*inch * (rows_per_page - 1))) / rows_per_page
    
    for page_start in range(0, total_products, labels_per_page):
        page_products = products_list[page_start:page_start + labels_per_page]
        
        # Create rows for this page
        for row_idx in range(rows_per_page):
            row_labels = []
            for col_idx in range(cols_per_page):
                product_idx = row_idx * cols_per_page + col_idx
                if product_idx < len(page_products):
                    product = page_products[product_idx]
                    
                    # Create label content
                    label_elements = []
                    
                    # Product Name
                    product_name = product.name[:25] + '...' if len(product.name) > 25 else product.name
                    label_elements.append(Paragraph(product_name, product_name_style))
                    label_elements.append(Spacer(1, 0.05*inch))
                    
                    # QR Code (optimized size)
                    qr_data = product.qr_code or product.sku or str(product.id)
                    try:
                        qr_img_buffer = generate_qr_code_image(qr_data, size=50)  # Smaller size
                        qr_img = Image(qr_img_buffer, width=0.5*inch, height=0.5*inch)
                        label_elements.append(qr_img)
                        label_elements.append(Spacer(1, 0.02*inch))
                        label_elements.append(Paragraph(f"QR: {qr_data[:12]}", code_style))  # Shorter text
                    except Exception as e:
                        label_elements.append(Paragraph(f"QR: {qr_data[:12]}", code_style))
                    
                    label_elements.append(Spacer(1, 0.02*inch))
                    
                    # Barcode (optimized)
                    barcode_data = product.barcode or product.sku or str(product.id)
                    try:
                        # Remove non-numeric characters for barcode (Code128 needs valid format)
                        barcode_clean = ''.join(c for c in barcode_data if c.isalnum() or c in '-_')
                        if len(barcode_clean) > 0:
                            barcode_img_buffer = generate_barcode_image(barcode_clean, width=100, height=20)  # Smaller
                            barcode_img = Image(barcode_img_buffer, width=1.0*inch, height=0.25*inch)
                            label_elements.append(barcode_img)
                            label_elements.append(Spacer(1, 0.02*inch))
                        label_elements.append(Paragraph(f"BC: {barcode_data[:12]}", code_style))  # Shorter text
                    except Exception as e:
                        label_elements.append(Paragraph(f"BC: {barcode_data[:12]}", code_style))
                    
                    label_elements.append(Spacer(1, 0.03*inch))
                    
                    # SKU
                    if product.sku:
                        label_elements.append(Paragraph(f"SKU: {product.sku[:12]}", sku_style))
                    
                    # Create table for label (centered content)
                    label_table = Table([[label_elements]], colWidths=[label_width], rowHeights=[label_height])
                    label_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 5),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),  # Border around label
                    ]))
                    
                    row_labels.append(label_table)
                else:
                    # Empty cell
                    empty_table = Table([['']], colWidths=[label_width], rowHeights=[label_height])
                    empty_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    row_labels.append(empty_table)
            
            # Add row to story
            if len(row_labels) > 0:
                row_table = Table([row_labels], colWidths=[label_width] * cols_per_page)
                row_table.setStyle(TableStyle([
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                story.append(row_table)
                story.append(Spacer(1, 0.05*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

