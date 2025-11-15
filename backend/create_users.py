#!/usr/bin/env python
"""
Quick script to create dummy users for login
Run with: python manage.py shell < create_users.py
Or: python manage.py shell
Then paste the code below
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_system.settings')
django.setup()

from accounts.models import User, Role

# Create roles if not exist
Role.objects.get_or_create(name='admin')
Role.objects.get_or_create(name='owner')
Role.objects.get_or_create(name='manager')
Role.objects.get_or_create(name='employee')

# Create admin user
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@pos.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
admin.set_password('admin123')
admin.save()
print(f"✅ Admin user {'created' if created else 'updated'}: username='admin', password='admin123'")

# Create owner user
owner, created = User.objects.get_or_create(
    username='owner',
    defaults={
        'email': 'owner@pos.com',
        'first_name': 'Owner',
        'last_name': 'User',
        'role': 'owner',
    }
)
owner.set_password('owner123')
owner.save()
print(f"✅ Owner user {'created' if created else 'updated'}: username='owner', password='owner123'")

# Create manager user
manager, created = User.objects.get_or_create(
    username='manager',
    defaults={
        'email': 'manager@pos.com',
        'first_name': 'Manager',
        'last_name': 'User',
        'role': 'manager',
    }
)
manager.set_password('manager123')
manager.save()
print(f"✅ Manager user {'created' if created else 'updated'}: username='manager', password='manager123'")

# Create employee user
employee, created = User.objects.get_or_create(
    username='employee',
    defaults={
        'email': 'employee@pos.com',
        'first_name': 'Employee',
        'last_name': 'User',
        'role': 'employee',
    }
)
employee.set_password('employee123')
employee.save()
print(f"✅ Employee user {'created' if created else 'updated'}: username='employee', password='employee123'")

print("\n" + "="*50)
print("✅ Users created successfully!")
print("="*50)
print("\nLogin Credentials:")
print("  Admin:    username='admin'    password='admin123'")
print("  Owner:    username='owner'    password='owner123'")
print("  Manager:  username='manager'  password='manager123'")
print("  Employee: username='employee' password='employee123'")
print("\nYou can now login to your application!")

