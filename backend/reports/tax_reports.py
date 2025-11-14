"""
Tax Report Generation
Tax by category, product, and summary reports
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from billing.models import Invoice, InvoiceItem
from products.models import Product, Category


class TaxReports:
    """Tax Report Generation"""
    
    @staticmethod
    def tax_by_category(date_from, date_to):
        """
        Generate tax report by category
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            dict with tax data by category
        """
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).prefetch_related('items__product__category')
        
        category_data = {}
        total_tax = Decimal('0.00')
        total_taxable = Decimal('0.00')
        
        for invoice in invoices:
            for item in invoice.items.all():
                category_name = item.product.category.name if item.product.category else 'Uncategorized'
                
                if category_name not in category_data:
                    category_data[category_name] = {
                        'category': category_name,
                        'total_quantity': 0,
                        'total_taxable_value': Decimal('0.00'),
                        'total_tax': Decimal('0.00'),
                        'tax_rate': item.tax_rate or Decimal('0.00'),
                        'invoices_count': 0
                    }
                
                item_taxable = (item.unit_price * item.quantity) - item.discount
                item_tax = item.tax_amount
                
                category_data[category_name]['total_quantity'] += item.quantity
                category_data[category_name]['total_taxable_value'] += item_taxable
                category_data[category_name]['total_tax'] += item_tax
                category_data[category_name]['invoices_count'] += 1
                
                total_taxable += item_taxable
                total_tax += item_tax
        
        # Convert to float for JSON
        for cat in category_data.values():
            cat['total_taxable_value'] = float(cat['total_taxable_value'])
            cat['total_tax'] = float(cat['total_tax'])
            cat['tax_rate'] = float(cat['tax_rate'])
        
        return {
            'report_type': 'Tax by Category',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'summary': {
                'total_taxable_value': float(total_taxable),
                'total_tax': float(total_tax),
                'categories_count': len(category_data)
            },
            'details': list(category_data.values())
        }
    
    @staticmethod
    def tax_by_product(date_from, date_to, product_id=None):
        """
        Generate tax report by product
        
        Args:
            date_from: Start date
            date_to: End date
            product_id: Product filter (optional)
        
        Returns:
            dict with tax data by product
        """
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).prefetch_related('items__product')
        
        product_data = {}
        total_tax = Decimal('0.00')
        total_taxable = Decimal('0.00')
        
        for invoice in invoices:
            for item in invoice.items.all():
                if product_id and item.product.id != product_id:
                    continue
                
                product_name = item.product.name
                product_sku = item.product.sku
                
                if product_name not in product_data:
                    product_data[product_name] = {
                        'product_name': product_name,
                        'product_sku': product_sku,
                        'total_quantity': 0,
                        'total_taxable_value': Decimal('0.00'),
                        'total_tax': Decimal('0.00'),
                        'tax_rate': item.tax_rate or Decimal('0.00'),
                        'invoices_count': 0
                    }
                
                item_taxable = (item.unit_price * item.quantity) - item.discount
                item_tax = item.tax_amount
                
                product_data[product_name]['total_quantity'] += item.quantity
                product_data[product_name]['total_taxable_value'] += item_taxable
                product_data[product_name]['total_tax'] += item_tax
                product_data[product_name]['invoices_count'] += 1
                
                total_taxable += item_taxable
                total_tax += item_tax
        
        # Convert to float for JSON
        for prod in product_data.values():
            prod['total_taxable_value'] = float(prod['total_taxable_value'])
            prod['total_tax'] = float(prod['total_tax'])
            prod['tax_rate'] = float(prod['tax_rate'])
        
        return {
            'report_type': 'Tax by Product',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'summary': {
                'total_taxable_value': float(total_taxable),
                'total_tax': float(total_tax),
                'products_count': len(product_data)
            },
            'details': list(product_data.values())
        }
    
    @staticmethod
    def tax_summary(date_from, date_to):
        """
        Generate tax summary report
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            dict with tax summary
        """
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).prefetch_related('items')
        
        total_sales = Decimal('0.00')
        total_taxable = Decimal('0.00')
        total_tax = Decimal('0.00')
        total_discount = Decimal('0.00')
        invoice_count = invoices.count()
        
        for invoice in invoices:
            total_sales += invoice.total_amount
            total_taxable += invoice.subtotal - invoice.discount_amount
            total_tax += invoice.tax_amount
            total_discount += invoice.discount_amount
        
        # Calculate tax rates breakdown
        tax_rates = {}
        for invoice in invoices:
            for item in invoice.items.all():
                rate = item.tax_rate or Decimal('0.00')
                rate_key = f"{rate}%"
                if rate_key not in tax_rates:
                    tax_rates[rate_key] = {
                        'rate': float(rate),
                        'taxable_value': Decimal('0.00'),
                        'tax_amount': Decimal('0.00')
                    }
                
                item_taxable = (item.unit_price * item.quantity) - item.discount
                item_tax = item.tax_amount
                
                tax_rates[rate_key]['taxable_value'] += item_taxable
                tax_rates[rate_key]['tax_amount'] += item_tax
        
        # Convert to float
        for rate_data in tax_rates.values():
            rate_data['taxable_value'] = float(rate_data['taxable_value'])
            rate_data['tax_amount'] = float(rate_data['tax_amount'])
        
        return {
            'report_type': 'Tax Summary',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'summary': {
                'total_invoices': invoice_count,
                'total_sales': float(total_sales),
                'total_taxable_value': float(total_taxable),
                'total_tax': float(total_tax),
                'total_discount': float(total_discount),
                'net_sales': float(total_sales - total_tax)
            },
            'tax_by_rate': list(tax_rates.values())
        }





