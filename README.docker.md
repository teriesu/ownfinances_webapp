# Docker Deployment Guide

This guide explains how to run the Finances webapp using Docker.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

## Development Setup

### 1. First Time Setup

```bash
# Make sure you're in the project directory
cd "/mnt/e/Personal Projects and study/Finances webapp"

# Build and start the containers
docker-compose up -d

# Check logs to ensure everything is running
docker-compose logs -f
```

The application will be available at `http://localhost:616`

### 2. Useful Commands

```bash
# Start the containers
docker-compose up -d

# Stop the containers
docker-compose down

# View logs
docker-compose logs -f web
docker-compose logs -f db

# Restart the web container
docker-compose restart web

# Run database migrations
docker-compose exec web flask db upgrade

# Access the database
docker-compose exec db psql -U postgres -d personalfinances

# Rebuild containers (after code changes)
docker-compose up -d --build

# Stop and remove everything (including volumes/data)
docker-compose down -v
```

### 3. Running Flask Commands

```bash
# Create a new migration
docker-compose exec web flask db migrate -m "Your migration message"

# Apply migrations
docker-compose exec web flask db upgrade

# Access Flask shell
docker-compose exec web flask shell

# Run custom Flask commands
docker-compose exec web flask <your-command>
```

## Production Deployment

### 1. Prepare Production Environment

```bash
# Copy the production environment file
cp .env.example .env.prod

# Edit .env.prod with production values
nano .env.prod
```

**Important**: Update these values in `.env.prod`:
- `DB_PASSWORD` - Use a strong password
- `SECRET_KEY` - Generate a secure random key
- `DB_HOST=db` (this is correct for Docker)

### 2. Deploy with Production Configuration

```bash
# Build and start production containers
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production containers
docker-compose -f docker-compose.prod.yml down
```

The production application will be available at `http://localhost:8000`

### 3. Production Commands

```bash
# Run migrations in production
docker-compose -f docker-compose.prod.yml exec web flask db upgrade

# View production logs
docker-compose -f docker-compose.prod.yml logs -f web

# Restart production services
docker-compose -f docker-compose.prod.yml restart web
```

## Database Backups

### Backup Database

```bash
# Development
docker-compose exec db pg_dump -U postgres personalfinances > backup_$(date +%Y%m%d_%H%M%S).sql

# Production
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres personalfinances > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database

```bash
# Development
docker-compose exec -T db psql -U postgres personalfinances < backup_file.sql

# Production
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres personalfinances < backup_file.sql
```

## Troubleshooting

### Database Connection Issues

If the web container can't connect to the database:

```bash
# Check if database is healthy
docker-compose ps

# Check database logs
docker-compose logs db

# Restart the database
docker-compose restart db
```

### Port Already in Use

If port 616 or 5432 is already in use:

1. Edit `docker-compose.yml`
2. Change the port mapping (e.g., `"617:5000"` for web or `"5433:5432"` for db)
3. Restart: `docker-compose up -d`

### Rebuild Everything

If you encounter persistent issues:

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose rm -f
docker rmi finances_webapp_web

# Rebuild from scratch
docker-compose up -d --build
```

### Check Container Status

```bash
# List all containers
docker-compose ps

# Check container health
docker inspect finances_web --format='{{.State.Health.Status}}'
docker inspect finances_db --format='{{.State.Health.Status}}'

# Access container shell
docker-compose exec web bash
docker-compose exec db bash
```

## Migrating from Local Setup

If you were running the app locally without Docker:

1. **Export your database** (if you have existing data):
   ```bash
   pg_dump -U postgres personalfinances > migration_backup.sql
   ```

2. **Start Docker containers**:
   ```bash
   docker-compose up -d
   ```

3. **Import your data**:
   ```bash
   docker-compose exec -T db psql -U postgres personalfinances < migration_backup.sql
   ```

4. **Stop your local Flask and PostgreSQL** to avoid port conflicts

## Environment Variables

The application uses these environment variables (defined in `.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USERNAME` | PostgreSQL username | postgres |
| `DB_PASSWORD` | PostgreSQL password | (required) |
| `DB_HOST` | Database host | localhost (db in Docker) |
| `DB_PORT` | Database port | 5432 |
| `DB_DATABASE` | Database name | personalfinances |
| `SECRET_KEY` | Flask secret key | (required) |

**Note**: When using Docker Compose, `DB_HOST` is automatically set to `db` (the service name).

## Notes

- The database data is persisted in a Docker volume, so it won't be lost when containers are stopped
- Use `docker-compose down -v` only if you want to delete all data
- For production, consider using a managed database service or separate database server
- The development setup includes hot-reload, so code changes are reflected automatically
