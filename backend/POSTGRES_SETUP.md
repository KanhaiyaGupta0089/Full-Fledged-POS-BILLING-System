# PostgreSQL Setup Guide

## Prerequisites

1. Install PostgreSQL on your system:
   - **Ubuntu/Debian**: `sudo apt-get install postgresql postgresql-contrib`
   - **macOS**: `brew install postgresql`
   - **Windows**: Download from https://www.postgresql.org/download/windows/

2. Start PostgreSQL service:
   - **Ubuntu/Debian**: `sudo systemctl start postgresql`
   - **macOS**: `brew services start postgresql`
   - **Windows**: PostgreSQL service should start automatically

## Database Setup

### 1. Create Database

```bash
# Login to PostgreSQL as postgres user
sudo -u postgres psql

# Or if you have a postgres user with password:
psql -U postgres -h localhost
```

### 2. Create Database and User

```sql
-- Create database
CREATE DATABASE pos_system;

-- Create user (optional, you can use postgres user)
CREATE USER pos_user WITH PASSWORD 'your_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pos_system TO pos_user;

-- Exit psql
\q
```

### 3. Update .env File

Create or update `backend/.env` file:

```env
# PostgreSQL Database
DATABASE_URL=postgresql://pos_user:your_password_here@localhost:5432/pos_system

# Or use postgres user directly:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pos_system
```

**Format**: `postgresql://username:password@host:port/database_name`

### 4. Install Python PostgreSQL Driver

The `psycopg2-binary` package is already in `requirements.txt`, but if you need to install it separately:

```bash
pip install psycopg2-binary
```

### 5. Run Migrations

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Troubleshooting

### Connection Error

If you get a connection error:
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify database exists: `psql -U postgres -l`
3. Check credentials in `.env` file
4. Verify PostgreSQL is listening on port 5432: `sudo netstat -tulpn | grep 5432`

### Permission Denied

If you get permission errors:
```sql
-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE pos_system TO your_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
```

### Reset Database (if needed)

```sql
-- Drop and recreate database
DROP DATABASE pos_system;
CREATE DATABASE pos_system;
```

Then run migrations again:
```bash
python manage.py migrate
```

## Quick Setup Script

For Ubuntu/Debian:

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql -c "CREATE DATABASE pos_system;"
sudo -u postgres psql -c "CREATE USER pos_user WITH PASSWORD 'pos_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pos_system TO pos_user;"

# Update .env file with:
# DATABASE_URL=postgresql://pos_user:pos_password@localhost:5432/pos_system
```

