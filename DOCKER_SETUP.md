# Docker Setup Guide for POS System

## Prerequisites

- Docker installed on your system
- Docker Compose installed

## Quick Start

### 1. Start Docker Services

```bash
# From project root directory
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis on port 6379
- PgAdmin on port 8080 (optional, for database management)

### 2. Configure Backend .env File

Copy the Docker environment file:

```bash
cd backend
cp .env.docker .env
```

Or create `.env` manually with:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL (Docker)
DATABASE_URL=postgresql://pos_user:12345678@localhost:5432/pos_system

# Redis (Docker)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. Setup Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Wait for database to be ready (takes a few seconds)
sleep 5

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Start Backend Server

```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### 5. Start Frontend (in another terminal)

```bash
cd frontend
npm install  # If not already done
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Docker Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Check service status
```bash
docker-compose ps
```

### Restart a service
```bash
docker-compose restart db
```

### Access PostgreSQL directly
```bash
docker-compose exec db psql -U pos_user -d pos_system
```

### Access Redis CLI
```bash
docker-compose exec redis redis-cli
```

## Database Management with PgAdmin

1. Open http://localhost:8080
2. Login with:
   - Email: `admin@possystem.com`
   - Password: `admin123`
3. Add server:
   - Name: `POS Database`
   - Host: `db` (or `localhost` if connecting from outside Docker)
   - Port: `5432`
   - Username: `pos_user`
   - Password: `12345678`

## Using Your Existing Docker Setup

If you want to use your existing Docker Compose file, you have two options:

### Option 1: Add POS services to existing docker-compose.yml

Add these services to your existing `docker-compose.yml`:

```yaml
  pos_db:
    image: postgres:14.0-alpine
    environment:
      - POSTGRES_DB=pos_system
      - POSTGRES_USER=pos_user
      - POSTGRES_PASSWORD=12345678
    ports:
      - "5433:5432"  # Different port to avoid conflict
    volumes:
      - pos_postgres_data:/var/lib/postgresql/data/
    networks:
      - app-network
```

Then update `.env`:
```env
DATABASE_URL=postgresql://pos_user:12345678@localhost:5433/pos_system
```

### Option 2: Use existing PostgreSQL container

If you want to use the existing `ez_delivery` database, update `.env`:

```env
DATABASE_URL=postgresql://ez_user:12345678@localhost:5432/ez_delivery
```

**Note**: It's recommended to use a separate database for the POS system.

## Troubleshooting

### Database connection error
- Check if container is running: `docker-compose ps`
- Check logs: `docker-compose logs db`
- Verify database is ready: `docker-compose exec db pg_isready -U pos_user`

### Port already in use
- If port 5432 is already used by your existing PostgreSQL, change the port in docker-compose.yml:
  ```yaml
  ports:
    - "5433:5432"  # Use different host port
  ```
- Update `.env` to use the new port

### Reset database
```bash
# Stop and remove volumes
docker-compose down -v

# Start again
docker-compose up -d

# Run migrations
python manage.py migrate
```

### View database data
```bash
docker-compose exec db psql -U pos_user -d pos_system -c "\dt"
```

## Production Considerations

For production:
1. Change default passwords
2. Use environment variables for sensitive data
3. Set up proper backups
4. Use Docker secrets or environment files
5. Set `DEBUG=False` in production

