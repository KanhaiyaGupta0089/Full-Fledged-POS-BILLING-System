"""
Profit & Loss Report Generation
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from billing.models import Invoice, InvoiceItem
from expenses.models import Expense
from purchases.models import PurchaseOrder, PurchaseOrderItem


class PLReports:
    """Profit & Loss Report Generation"""
    
    @staticmethod
    def profit_loss_statement(date_from, date_to):
        """
        Generate Profit & Loss statement
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            dict with P&L data
        """
        # Revenue (Sales)
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).prefetch_related('items')
        
        total_revenue = Decimal('0.00')
        total_cost_of_goods = Decimal('0.00')
        total_tax_collected = Decimal('0.00')
        total_discount_given = Decimal('0.00')
        
        # Calculate revenue and COGS
        for invoice in invoices:
            total_revenue += invoice.total_amount
            total_tax_collected += invoice.tax_amount
            total_discount_given += invoice.discount_amount
            
            # Calculate COGS (Cost of Goods Sold)
            for item in invoice.items.all():
                # Use purchase price or cost price
                cost_price = item.product.purchase_price or item.product.cost_price or Decimal('0.00')
                total_cost_of_goods += cost_price * item.quantity
        
        # Expenses
        expenses = Expense.objects.filter(
            is_approved=True,
            expense_date__gte=date_from,
            expense_date__lte=date_to
        )
        
        total_expenses = expenses.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Categorize expenses
        expense_by_category = {}
        for expense in expenses:
            category_name = expense.category.name if expense.category else 'Uncategorized'
            if category_name not in expense_by_category:
                expense_by_category[category_name] = Decimal('0.00')
            expense_by_category[category_name] += expense.total_amount
        
        # Calculate profit
        gross_profit = total_revenue - total_cost_of_goods - total_tax_collected
        net_profit = gross_profit - total_expenses
        
        # Convert to float for JSON
        expense_by_category_float = {
            k: float(v) for k, v in expense_by_category.items()
        }
        
        return {
            'report_type': 'Profit & Loss Statement',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'revenue': {
                'total_sales': float(total_revenue),
                'tax_collected': float(total_tax_collected),
                'discount_given': float(total_discount_given),
                'net_revenue': float(total_revenue - total_tax_collected)
            },
            'cost_of_goods_sold': {
                'total_cogs': float(total_cost_of_goods),
                'gross_profit': float(gross_profit),
                'gross_profit_margin': float((gross_profit / total_revenue * 100) if total_revenue > 0 else 0)
            },
            'expenses': {
                'total_expenses': float(total_expenses),
                'by_category': expense_by_category_float
            },
            'net_profit': {
                'net_profit': float(net_profit),
                'net_profit_margin': float((net_profit / total_revenue * 100) if total_revenue > 0 else 0)
            },
            'summary': {
                'total_revenue': float(total_revenue),
                'total_cogs': float(total_cost_of_goods),
                'gross_profit': float(gross_profit),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit)
            }
        }
    
    @staticmethod
    def revenue_breakdown(date_from, date_to):
        """
        Generate revenue breakdown
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            dict with revenue breakdown
        """
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).prefetch_related('items__product__category')
        
        revenue_by_category = {}
        revenue_by_payment_method = {}
        daily_revenue = {}
        
        for invoice in invoices:
            # By payment method
            method = invoice.payment_method
            if method not in revenue_by_payment_method:
                revenue_by_payment_method[method] = Decimal('0.00')
            revenue_by_payment_method[method] += invoice.total_amount
            
            # By date
            date = invoice.created_at.date()
            if date not in daily_revenue:
                daily_revenue[date] = Decimal('0.00')
            daily_revenue[date] += invoice.total_amount
            
            # By category
            for item in invoice.items.all():
                category_name = item.product.category.name if item.product.category else 'Uncategorized'
                if category_name not in revenue_by_category:
                    revenue_by_category[category_name] = Decimal('0.00')
                revenue_by_category[category_name] += item.total
        
        # Convert to float
        revenue_by_category_float = {k: float(v) for k, v in revenue_by_category.items()}
        revenue_by_payment_method_float = {k: float(v) for k, v in revenue_by_payment_method.items()}
        daily_revenue_float = {str(k): float(v) for k, v in daily_revenue.items()}
        
        return {
            'report_type': 'Revenue Breakdown',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'by_category': revenue_by_category_float,
            'by_payment_method': revenue_by_payment_method_float,
            'daily_revenue': daily_revenue_float
        }
    
    @staticmethod
    def expense_breakdown(date_from, date_to):
        """
        Generate expense breakdown
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            dict with expense breakdown
        """
        expenses = Expense.objects.filter(
            is_approved=True,
            expense_date__gte=date_from,
            expense_date__lte=date_to
        ).select_related('category')
        
        expense_by_category = {}
        expense_by_payment_method = {}
        daily_expenses = {}
        
        for expense in expenses:
            # By category
            category_name = expense.category.name if expense.category else 'Uncategorized'
            if category_name not in expense_by_category:
                expense_by_category[category_name] = Decimal('0.00')
            expense_by_category[category_name] += expense.total_amount
            
            # By payment method
            method = expense.payment_method
            if method not in expense_by_payment_method:
                expense_by_payment_method[method] = Decimal('0.00')
            expense_by_payment_method[method] += expense.total_amount
            
            # By date
            date = expense.expense_date
            if date not in daily_expenses:
                daily_expenses[date] = Decimal('0.00')
            daily_expenses[date] += expense.total_amount
        
        # Convert to float
        expense_by_category_float = {k: float(v) for k, v in expense_by_category.items()}
        expense_by_payment_method_float = {k: float(v) for k, v in expense_by_payment_method.items()}
        daily_expenses_float = {str(k): float(v) for k, v in daily_expenses.items()}
        
        return {
            'report_type': 'Expense Breakdown',
            'period': f"{date_from} to {date_to}",
            'generated_at': timezone.now(),
            'by_category': expense_by_category_float,
            'by_payment_method': expense_by_payment_method_float,
            'daily_expenses': daily_expenses_float
        }





