# Generated manually to add missing Customer fields
from django.db import migrations, models
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_customercommunication_customerpurchasehistory_and_more'),
    ]

    operations = [
        # Add alternate_phone if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS alternate_phone VARCHAR(15) DEFAULT '';",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS alternate_phone;"
        ),
        # Add city if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS city VARCHAR(100) DEFAULT '';",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS city;"
        ),
        # Add state if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS state VARCHAR(100) DEFAULT '';",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS state;"
        ),
        # Add pincode if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS pincode VARCHAR(10) DEFAULT '';",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS pincode;"
        ),
        # Add pan if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS pan VARCHAR(10) DEFAULT '';",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS pan;"
        ),
        # Add customer_type if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_type VARCHAR(20) DEFAULT 'regular';",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS customer_type;"
        ),
        # Add credit_limit if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS credit_limit NUMERIC(10, 2) DEFAULT 0.00;",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS credit_limit;"
        ),
        # Add loyalty_points if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS loyalty_points INTEGER DEFAULT 0;",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS loyalty_points;"
        ),
        # Add total_purchases if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_purchases NUMERIC(12, 2) DEFAULT 0.00;",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS total_purchases;"
        ),
        # Add total_orders if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_orders INTEGER DEFAULT 0;",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS total_orders;"
        ),
        # Add last_purchase_date if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_purchase_date TIMESTAMP NULL;",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS last_purchase_date;"
        ),
        # Add date_of_birth if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS date_of_birth DATE NULL;",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS date_of_birth;"
        ),
        # Add anniversary_date if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS anniversary_date DATE NULL;",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS anniversary_date;"
        ),
        # Add notes if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT '';",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS notes;"
        ),
        # Add is_blacklisted if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS is_blacklisted BOOLEAN DEFAULT FALSE;",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS is_blacklisted;"
        ),
        # Add blacklist_reason if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE customers ADD COLUMN IF NOT EXISTS blacklist_reason TEXT DEFAULT '';",
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS blacklist_reason;"
        ),
        # Add created_by_id if it doesn't exist (Foreign Key)
        migrations.RunSQL(
            sql="""
            DO $$
            DECLARE
                user_table_name TEXT;
            BEGIN
                -- Get the actual user table name (it's 'users')
                user_table_name := 'users';
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='customers' AND column_name='created_by_id'
                ) THEN
                    ALTER TABLE customers ADD COLUMN created_by_id BIGINT NULL;
                    
                    -- Add foreign key constraint if user table exists
                    IF user_table_name IS NOT NULL THEN
                        EXECUTE format('ALTER TABLE customers ADD CONSTRAINT customers_created_by_id_fk 
                            FOREIGN KEY (created_by_id) REFERENCES %I(id) 
                            ON DELETE SET NULL', user_table_name);
                    END IF;
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE customers DROP COLUMN IF EXISTS created_by_id;"
        ),
        # Update phone to allow NULL and be unique (handle duplicates first)
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Remove NOT NULL constraint if exists
                ALTER TABLE customers ALTER COLUMN phone DROP NOT NULL;
                
                -- Clean up duplicate phone numbers by setting them to NULL
                UPDATE customers c1
                SET phone = NULL
                WHERE phone IS NOT NULL AND phone != ''
                AND EXISTS (
                    SELECT 1 FROM customers c2 
                    WHERE c2.id < c1.id 
                    AND c2.phone = c1.phone 
                    AND c2.phone IS NOT NULL 
                    AND c2.phone != ''
                );
                
                -- Add unique constraint if not exists
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'customers_phone_key'
                ) THEN
                    CREATE UNIQUE INDEX customers_phone_key ON customers(phone) WHERE phone IS NOT NULL AND phone != '';
                END IF;
            END $$;
            """,
            reverse_sql="-- Reverse not needed"
        ),
    ]

