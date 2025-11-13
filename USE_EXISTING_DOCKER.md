# Using Your Existing Docker Setup

Since you already have a Docker Compose file with PostgreSQL, you have two options:

## Option 1: Add POS Database to Your Existing Docker Compose

Add this service to your existing `docker-compose.yml`:

```yaml
  pos_db:
    image: postgres:14.0-alpine
    container_name: pos_postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=pos_system
      - POSTGRES_USER=pos_user
      - POSTGRES_PASSWORD=12345678
    ports:
      - "5433:5432"  # Different port to avoid conflict with your existing db
    volumes:
      - pos_postgres_data:/var/lib/postgresql/data/
    networks:
      - app-network
```

And add to volumes:
```yaml
volumes:
  postgres_data:
  pos_postgres_data:  # Add this
  pgadmin-data:
  mongo_database:
  mysql_data:
```

Then update `backend/.env`:
```env
DATABASE_URL=postgresql://pos_user:12345678@localhost:5433/pos_system
```

## Option 2: Use Your Existing PostgreSQL Container

You can use your existing `ez_delivery` database. Update `backend/.env`:

```env
DATABASE_URL=postgresql://ez_user:12345678@localhost:5432/ez_delivery
```

**Note**: It's recommended to create a separate database for the POS system.

### Create POS Database in Existing Container

```bash
# Access your existing PostgreSQL container
docker-compose exec db psql -U ez_user -d ez_delivery

# Or if using your existing docker-compose file:
docker-compose -f your-docker-compose.yml exec db psql -U ez_user -d ez_delivery
```

Then in PostgreSQL:
```sql
-- Create new database
CREATE DATABASE pos_system;

-- Create user (optional, can use ez_user)
CREATE USER pos_user WITH PASSWORD '12345678';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pos_system TO pos_user;
\q
```

Update `backend/.env`:
```env
DATABASE_URL=postgresql://pos_user:12345678@localhost:5432/pos_system
```

## Option 3: Use Separate Docker Compose File

Keep the POS system's `docker-compose.yml` separate and run both:

```bash
# Start your existing services
docker-compose -f your-existing-file.yml up -d

# Start POS services (on different ports)
docker-compose -f docker-compose.yml up -d
```

## Quick Setup Steps

1. **Start your existing Docker services:**
   ```bash
   docker-compose -f your-file.yml up -d
   ```

2. **Create POS database** (if using existing PostgreSQL):
   ```bash
   docker-compose -f your-file.yml exec db psql -U ez_user -d ez_delivery -c "CREATE DATABASE pos_system;"
   ```

3. **Create backend/.env file:**
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=postgresql://ez_user:12345678@localhost:5432/pos_system
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Run migrations:**
   ```bash
   cd backend
   source venv/bin/activate
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Recommended Approach

**Best Practice**: Use Option 1 - Add a separate POS database to your existing Docker Compose file. This keeps everything organized and allows you to manage both systems together.

## Port Conflicts

If port 5432 is already in use by your existing PostgreSQL:
- Use port 5433 for POS database (as shown in Option 1)
- Or use a different port mapping: `"5434:5432"`

## Network Configuration

Make sure both databases are on the same network (`app-network`) if you need them to communicate, or keep them separate for isolation.

