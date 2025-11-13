# Quick Start with Docker

## 🚀 Fastest Way to Get Started

### Step 1: Start Docker Services

```bash
# From project root
docker-compose up -d
```

Wait a few seconds for PostgreSQL to be ready.

### Step 2: Setup Backend Environment

```bash
cd backend

# Copy Docker environment file
cp .env.docker .env

# Or create .env manually with:
# DATABASE_URL=postgresql://pos_user:12345678@localhost:5432/pos_system
# REDIS_URL=redis://localhost:6379/0
```

### Step 3: Setup Python Environment

```bash
# Create virtual environment (if not exists)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Run Migrations

```bash
# Wait for database (if just started)
sleep 5

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 5: Start Development Servers

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

### Step 6: Access Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- PgAdmin: http://localhost:8080 (admin@possystem.com / admin123)

## 🐳 Docker Services

- **PostgreSQL**: `localhost:5432`
  - Database: `pos_system`
  - User: `pos_user`
  - Password: `12345678`

- **Redis**: `localhost:6379`

- **PgAdmin**: `localhost:8080`
  - Email: `admin@possystem.com`
  - Password: `admin123`

## 📝 Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f db

# Restart database
docker-compose restart db

# Access PostgreSQL
docker-compose exec db psql -U pos_user -d pos_system
```

## ⚠️ Using Your Existing Docker Setup

If you already have PostgreSQL running on port 5432, you can:

1. **Use a different port** in `docker-compose.yml`:
   ```yaml
   ports:
     - "5433:5432"  # Use 5433 instead
   ```

2. **Use your existing database** by updating `.env`:
   ```env
   DATABASE_URL=postgresql://ez_user:12345678@localhost:5432/ez_delivery
   ```

3. **Add POS database to your existing docker-compose.yml**:
   ```yaml
   pos_db:
     image: postgres:14.0-alpine
     environment:
       - POSTGRES_DB=pos_system
       - POSTGRES_USER=pos_user
       - POSTGRES_PASSWORD=12345678
     ports:
       - "5433:5432"
     networks:
       - app-network
   ```

## 🔧 Troubleshooting

**Database not ready?**
```bash
# Check if running
docker-compose ps

# Check logs
docker-compose logs db

# Wait and retry
sleep 10
python manage.py migrate
```

**Port conflict?**
- Change port in docker-compose.yml
- Or stop existing PostgreSQL: `docker-compose -f your-file.yml down`

**Reset everything?**
```bash
docker-compose down -v
docker-compose up -d
python manage.py migrate
```

