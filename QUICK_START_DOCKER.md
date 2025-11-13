# Quick Start with Your Existing Docker Setup

Since you already have PostgreSQL running in Docker, here's the fastest way to get started:

## 🚀 Quick Setup (Using Your Existing PostgreSQL)

### Step 1: Create POS Database in Your Existing Container

```bash
# Access your existing PostgreSQL container
docker-compose -f your-docker-compose.yml exec db psql -U ez_user -d ez_delivery

# Or if your container name is different:
docker ps  # Find your PostgreSQL container name
docker exec -it <container_name> psql -U ez_user -d ez_delivery
```

In PostgreSQL prompt:
```sql
-- Create POS database
CREATE DATABASE pos_system;

-- Create user (optional, can use ez_user)
CREATE USER pos_user WITH PASSWORD '12345678';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pos_system TO pos_user;
\q
```

### Step 2: Create Backend .env File

```bash
cd backend
nano .env  # or your preferred editor
```

Add this content:
```env
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Use your existing PostgreSQL (port 5432)
DATABASE_URL=postgresql://pos_user:12345678@localhost:5432/pos_system

# Or use ez_user directly:
# DATABASE_URL=postgresql://ez_user:12345678@localhost:5432/pos_system

# Redis (you already have this)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 3: Run Migrations

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 4: Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # First time only
npm run dev
```

## ✅ You're Done!

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## 🔄 Alternative: Use Separate Docker Compose

If you prefer to keep POS system separate, use the provided `docker-compose.yml` which uses port 5433:

```bash
# Start POS services (on port 5433)
docker-compose up -d

# Update .env to use port 5433
DATABASE_URL=postgresql://pos_user:12345678@localhost:5433/pos_system
```

## 📝 Database Connection Details

**Your Existing Setup:**
- Host: `localhost`
- Port: `5432`
- Database: `ez_delivery` (or create `pos_system`)
- User: `ez_user`
- Password: `12345678`

**POS System (if using separate Docker):**
- Host: `localhost`
- Port: `5433` (to avoid conflict)
- Database: `pos_system`
- User: `pos_user`
- Password: `12345678`

## 🐛 Troubleshooting

**Port conflict?**
- Use port 5433 for POS database (already configured in docker-compose.yml)
- Or use your existing PostgreSQL on port 5432

**Can't connect?**
- Check your existing PostgreSQL is running: `docker ps`
- Verify database exists: `docker exec -it <container> psql -U ez_user -l`
- Check credentials in `.env` file

**Migrations fail?**
- Make sure database exists
- Check database user has proper permissions
- Verify connection string in `.env`

