# Database Setup Instructions

## Step 1: Create PostgreSQL Database

First, you need to create the PostgreSQL database. Run these commands:

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Or if you have a postgres user with password:
psql -U postgres -h localhost
```

Then in the PostgreSQL prompt:

```sql
-- Create database
CREATE DATABASE pos_system;

-- Create user (optional - you can use postgres user directly)
CREATE USER pos_user WITH PASSWORD 'your_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pos_system TO pos_user;

-- Exit
\q
```

## Step 2: Update .env File

Create or update `backend/.env` file with your PostgreSQL credentials:

```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/pos_system

# Or if you created a separate user:
# DATABASE_URL=postgresql://pos_user:your_password@localhost:5432/pos_system

# Redis (optional for now)
REDIS_URL=redis://localhost:6379/0

# Email (optional for now)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Step 3: Run Migrations

After setting up the database and .env file:

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Quick Setup (If PostgreSQL is already installed)

If PostgreSQL is already running and you know the postgres password:

```bash
# Create database
sudo -u postgres createdb pos_system

# Update .env with:
# DATABASE_URL=postgresql://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/pos_system

# Run migrations
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

## Troubleshooting

### If you get "password authentication failed"
- Check your PostgreSQL password
- Verify the user exists: `psql -U postgres -l`
- Try resetting postgres password: `sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'newpassword';"`

### If you get "database does not exist"
- Create the database: `sudo -u postgres createdb pos_system`

### If you get "permission denied"
- Grant privileges: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pos_system TO postgres;"`

