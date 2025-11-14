"""
GST Report Generation
GSTR-1 (Outward Supplies) and GSTR-2 (Inward Supplies)
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from billing.models import Invoice, InvoiceItem
from purchases.models import PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GRNItem


class GSTReports:
    """GST Report Generation"""
    
    @staticmethod
    def gstr1_outward_supplies(date_from, date_to, gstin=None):
        """
        Generate GSTR-1 (Outward Supplies) report
        
        Args:
            date_from: Start date
            date_to: End date
            gstin: Customer GSTIN filter (optional)
        
        Returns:
            dict with GSTR-1 data
        """
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).select_related('customer').prefetch_related('items')
        
        if gstin:
            invoices = invoices.filter(customer__gstin=gstin)
        
        # Group by GSTIN
        gstin_data = {}
        total_taxable_value = Decimal('0.00')
        total_igst = Decimal('0.00')
        total_cgst = Decimal('0.00')
        total_sgst = Decimal('0.00')
        total_cess = Decimal('0.00')
        
        for invoice in invoices:
            customer_gstin = invoice.customer.gstin if invoice.customer and invoice.customer.gstin else 'UNREGISTERED'
            
            if customer_gstin not in gstin_data:
                gstin_data[customer_gstin] = {
                    'gstin': customer_gstin,
                    'customer_name': invoice.customer.name if invoice.customer else invoice.customer_name,
                    'invoices': [],
                    'total_taxable_value': Decimal('0.00'),
                    'total_igst': Decimal('0.00'),
                    'total_cgst': Decimal('0.00'),
                    'total_sgst': Decimal('0.00'),
                    'total_cess': Decimal('0.00'),
                }
            
            # Calculate tax breakdown
            invoice_taxable = invoice.subtotal - invoice.discount_amount
            invoice_tax = invoice.tax_amount
            
            # Assume 50% CGST and 50% SGST for same state, 100% IGST for different state
            # This is simplified - in real scenario, check if customer state matches business state
            cgst = invoice_tax / 2
            sgst = invoice_tax / 2
            igst = Decimal('0.00')
            
            gstin_data[customer_gstin]['invoices'].append({
                'invoice_number': invoice.invoice_number,
                'date': invoice.created_at.date(),
                'taxable_value': invoice_taxable,
                'tax_amount': invoice_tax,
                'cgst': cgst,
                'sgst': sgst,
                'igst': igst,
            })
            
            gstin_data[customer_gstin]['total_taxable_value'] += invoice_taxable
            gstin_data[customer_gstin]['total_cgst'] += cgst
            gstin_data[customer_gstin]['total_sgst'] += sgst
            gstin_data[customer_gstin]['total_igst'] += igst
            
            total_taxable_value += invoice_taxable
            total_cgst += cgst
            total_sgst += sgst
            total_igst += igst
        
        return {
            'report_type': 'GSTR-1',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'summary': {
                'total_invoices': invoices.count(),
                'total_taxable_value': float(total_taxable_value),
                'total_cgst': float(total_cgst),
                'total_sgst': float(total_sgst),
                'total_igst': float(total_igst),
                'total_tax': float(total_cgst + total_sgst + total_igst),
            },
            'details': list(gstin_data.values())
        }
    
    @staticmethod
    def gstr2_inward_supplies(date_from, date_to, supplier_gstin=None):
        """
        Generate GSTR-2 (Inward Supplies) report
        
        Args:
            date_from: Start date
            date_to: End date
            supplier_gstin: Supplier GSTIN filter (optional)
        
        Returns:
            dict with GSTR-2 data
        """
        grns = GoodsReceiptNote.objects.filter(
            is_verified=True,
            received_at__date__gte=date_from,
            received_at__date__lte=date_to
        ).select_related('purchase_order__supplier').prefetch_related('items')
        
        if supplier_gstin:
            grns = grns.filter(purchase_order__supplier__gstin=supplier_gstin)
        
        # Group by Supplier GSTIN
        gstin_data = {}
        total_taxable_value = Decimal('0.00')
        total_igst = Decimal('0.00')
        total_cgst = Decimal('0.00')
        total_sgst = Decimal('0.00')
        total_cess = Decimal('0.00')
        
        for grn in grns:
            supplier = grn.purchase_order.supplier if grn.purchase_order else None
            supplier_gstin = supplier.gstin if supplier and supplier.gstin else 'UNREGISTERED'
            
            if supplier_gstin not in gstin_data:
                gstin_data[supplier_gstin] = {
                    'gstin': supplier_gstin,
                    'supplier_name': supplier.name if supplier else 'Unknown',
                    'grns': [],
                    'total_taxable_value': Decimal('0.00'),
                    'total_igst': Decimal('0.00'),
                    'total_cgst': Decimal('0.00'),
                    'total_sgst': Decimal('0.00'),
                    'total_cess': Decimal('0.00'),
                }
            
            # Calculate tax from GRN items
            grn_taxable = Decimal('0.00')
            grn_tax = Decimal('0.00')
            
            for item in grn.items.all():
                item_total = item.unit_price * item.quantity_received
                item_tax = (item_total * item.tax_rate) / 100 if item.tax_rate else Decimal('0.00')
                grn_taxable += item_total
                grn_tax += item_tax
            
            # Assume 50% CGST and 50% SGST for same state
            cgst = grn_tax / 2
            sgst = grn_tax / 2
            igst = Decimal('0.00')
            
            gstin_data[supplier_gstin]['grns'].append({
                'grn_number': grn.grn_number,
                'po_number': grn.purchase_order.po_number if grn.purchase_order else '',
                'date': grn.received_at.date() if grn.received_at else grn.created_at.date(),
                'taxable_value': grn_taxable,
                'tax_amount': grn_tax,
                'cgst': cgst,
                'sgst': sgst,
                'igst': igst,
            })
            
            gstin_data[supplier_gstin]['total_taxable_value'] += grn_taxable
            gstin_data[supplier_gstin]['total_cgst'] += cgst
            gstin_data[supplier_gstin]['total_sgst'] += sgst
            gstin_data[supplier_gstin]['total_igst'] += igst
            
            total_taxable_value += grn_taxable
            total_cgst += cgst
            total_sgst += sgst
            total_igst += igst
        
        return {
            'report_type': 'GSTR-2',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'summary': {
                'total_grns': grns.count(),
                'total_taxable_value': float(total_taxable_value),
                'total_cgst': float(total_cgst),
                'total_sgst': float(total_sgst),
                'total_igst': float(total_igst),
                'total_tax': float(total_cgst + total_sgst + total_igst),
            },
            'details': list(gstin_data.values())
        }
    
    @staticmethod
    def gst_summary(date_from, date_to):
        """
        Generate GST Summary (GSTR-1 + GSTR-2)
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            dict with GST summary
        """
        gstr1 = GSTReports.gstr1_outward_supplies(date_from, date_to)
        gstr2 = GSTReports.gstr2_inward_supplies(date_from, date_to)
        
        # Calculate net GST payable
        outward_tax = gstr1['summary']['total_tax']
        inward_tax = gstr2['summary']['total_tax']
        net_gst_payable = outward_tax - inward_tax
        
        return {
            'report_type': 'GST Summary',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'outward_supplies': gstr1['summary'],
            'inward_supplies': gstr2['summary'],
            'net_gst_payable': net_gst_payable,
            'gstr1_details': gstr1['details'],
            'gstr2_details': gstr2['details']
        }





