# Next Steps - PostgreSQL Setup

## ✅ What's Done

1. ✅ Migrations created for `accounts` app
2. ✅ Database configuration updated for PostgreSQL
3. ✅ Custom User model with roles ready
4. ✅ Docker Compose file created

## 🔧 What You Need to Do

### Option A: Using Docker (Recommended)

**Step 1: Start Docker Services**

```bash
# From project root
docker-compose up -d
```

**Step 2: Create .env file**

```bash
cd backend
cp .env.docker .env
# Or create manually with DATABASE_URL=postgresql://pos_user:12345678@localhost:5432/pos_system
```

**Step 3: Run Migrations**

```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

### Option B: Using Your Existing Docker Setup

See `USE_EXISTING_DOCKER.md` for instructions on using your existing PostgreSQL container.

### Option C: Local PostgreSQL Installation

**Step 1: Set Up PostgreSQL Database**

If PostgreSQL is already installed, create the database:

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Or if you have a password:
psql -U postgres -h localhost
```

Then run:
```sql
CREATE DATABASE pos_system;
\q
```

**Option B: Install PostgreSQL (if not installed)**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres createdb pos_system
```

### Step 2: Create .env File

Create `backend/.env` file with your PostgreSQL credentials:

```bash
cd backend
nano .env  # or use your preferred editor
```

Add this content (update with your actual PostgreSQL password):

```env
SECRET_KEY=django-insecure-change-this-in-production-use-random-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL=postgresql://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/pos_system

# Redis (optional for now)
REDIS_URL=redis://localhost:6379/0

# Email (optional for now)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Important**: Replace `YOUR_POSTGRES_PASSWORD` with your actual PostgreSQL password.

### Step 3: Run Migrations

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Apply migrations to create tables
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

When creating superuser, you'll be asked for:
- Username
- Email (optional)
- Password
- Role (select: admin, owner, manager, or employee)

### Step 4: Test Login

1. Start backend server:
```bash
python manage.py runserver
```

2. Start frontend (in another terminal):
```bash
cd frontend
npm run dev
```

3. Open http://localhost:5173 and test login with your superuser credentials.

## 🔍 Troubleshooting

### "password authentication failed"
- Check your PostgreSQL password in `.env`
- Try: `sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'newpassword';"`
- Update `.env` with the new password

### "database does not exist"
- Create it: `sudo -u postgres createdb pos_system`

### "connection refused"
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Start it: `sudo systemctl start postgresql`

### "no such table: users"
- Run migrations: `python manage.py migrate`

## 📝 Quick Reference

**Database URL Format:**
```
postgresql://username:password@host:port/database_name
```

**Example:**
```
postgresql://postgres:mypassword@localhost:5432/pos_system
```

## ✅ Verification

After setup, verify everything works:

```bash
# Check database connection
python manage.py dbshell

# List tables
\dt

# Exit
\q
```

You should see tables like:
- `users`
- `user_roles`
- `django_migrations`
- etc.

