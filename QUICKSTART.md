# 🚀 Quick Start - Running with Docker

This is the fastest way to get your application running!

## Option 1: Automated Setup (Recommended)

### On Linux/WSL/Mac:
```bash
./start-docker.sh
```

### On Windows:
```cmd
start-docker.bat
```

That's it! The script will:
- Check if Docker is installed
- Create `.env` if it doesn't exist
- Build and start all containers
- Run database migrations
- Show you the application URL

## Option 2: Manual Setup

### 1. Start the containers
```bash
docker-compose up -d
```

### 2. Run database migrations
```bash
docker-compose exec web flask db upgrade
```

### 3. Access the application
Open your browser to: **http://localhost:616**

## Option 3: Using Make (Quick Commands)

If you have `make` installed:

```bash
make up          # Start everything
make logs        # View logs
make down        # Stop everything
make help        # See all available commands
```

## 📝 Common Commands

```bash
# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart after code changes
docker-compose restart web

# Access database
docker-compose exec db psql -U postgres -d personalfinances

# Run Flask commands
docker-compose exec web flask shell
```

## 🆘 Troubleshooting

### Port already in use?
Edit `docker-compose.yml` and change the port:
```yaml
ports:
  - "617:5000"  # Changed from 616 to 617
```

### Database connection issues?
```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs db
docker-compose logs web

# Restart everything
docker-compose restart
```

### Need to reset everything?
```bash
docker-compose down -v  # WARNING: This deletes all data!
docker-compose up -d --build
```

## 📚 More Information

For detailed documentation, see [README.docker.md](README.docker.md)
