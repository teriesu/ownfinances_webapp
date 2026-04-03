# 🚀 Docker Quick Reference Card

## One-Command Start
```bash
./start-docker.sh          # Linux/WSL/Mac
start-docker.bat           # Windows
```

## Essential Commands

### Starting & Stopping
| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all containers |
| `docker-compose down` | Stop all containers |
| `docker-compose restart` | Restart all containers |
| `docker-compose restart web` | Restart only web container |
| `docker-compose ps` | Show container status |

### Logs & Debugging
| Command | Description |
|---------|-------------|
| `docker-compose logs -f` | View all logs (live) |
| `docker-compose logs -f web` | View web logs only |
| `docker-compose logs -f db` | View database logs only |
| `docker-compose logs --tail=100 web` | Last 100 lines |

### Database Operations
| Command | Description |
|---------|-------------|
| `docker-compose exec db psql -U postgres -d personalfinances` | Database shell |
| `docker-compose exec web flask db upgrade` | Run migrations |
| `docker-compose exec web flask db migrate -m "msg"` | Create migration |
| `docker-compose exec -T db pg_dump -U postgres personalfinances > backup.sql` | Backup |
| `docker-compose exec -T db psql -U postgres personalfinances < backup.sql` | Restore |

### Container Access
| Command | Description |
|---------|-------------|
| `docker-compose exec web bash` | Web container shell |
| `docker-compose exec db bash` | Database container shell |
| `docker-compose exec web flask shell` | Flask shell |
| `docker-compose exec web env` | View environment variables |

### Rebuilding
| Command | Description |
|---------|-------------|
| `docker-compose up -d --build` | Rebuild and start |
| `docker-compose build` | Build images only |
| `docker-compose down -v` | Stop and delete volumes (⚠️ deletes data!) |

## Make Commands (Shortcuts)

| Command | What It Does |
|---------|-------------|
| `make up` | Start everything |
| `make down` | Stop everything |
| `make logs` | View logs |
| `make logs-web` | View web logs |
| `make logs-db` | View database logs |
| `make shell` | Web container shell |
| `make db-shell` | Database shell |
| `make migrate` | Run migrations |
| `make migrate-create MSG="msg"` | Create migration |
| `make backup` | Backup database |
| `make restore FILE=backup.sql` | Restore database |
| `make rebuild` | Rebuild everything |
| `make clean` | Remove all containers/volumes |
| `make prod` | Start production |
| `make help` | Show all commands |

## URLs

| Service | URL |
|---------|-----|
| Development App | http://localhost:616 |
| Production App | http://localhost:8000 |
| Health Check | http://localhost:616/health |

## Health Check

```bash
# Quick health check
curl http://localhost:616/health

# Expected response when healthy:
{"status": "healthy", "database": "connected"}
```

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| Port already in use | Edit `docker-compose.yml`, change `"616:5000"` to `"617:5000"` |
| Can't connect to database | `docker-compose restart` |
| Code changes not reflected | `docker-compose restart web` (dev mode has hot-reload) |
| Need fresh start | `docker-compose down && docker-compose up -d` |
| Complete reset | `docker-compose down -v && docker-compose up -d --build` |
| Docker not found | See [DOCKER-SETUP.md](DOCKER-SETUP.md) |

## File Locations

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Development config |
| `docker-compose.prod.yml` | Production config |
| `Dockerfile` | Development image |
| `Dockerfile.prod` | Production image |
| `.env` | Environment variables |
| `start-docker.sh` | Quick start (Linux/Mac/WSL) |
| `Makefile` | Shortcut commands |

## Production Deployment

```bash
# 1. Create production env
cp .env.example .env.prod
nano .env.prod  # Update passwords and keys

# 2. Deploy
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Check status
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

## Environment Variables

| Variable | Purpose | Docker Value |
|----------|---------|--------------|
| `DB_HOST` | Database host | `db` (auto-set) |
| `DB_USERNAME` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | From `.env` |
| `DB_DATABASE` | Database name | `personalfinances` |
| `DB_PORT` | Database port | `5432` |

## Volume Management

| Command | Description |
|---------|-------------|
| `docker volume ls` | List all volumes |
| `docker volume inspect finances_webapp_postgres_data` | Inspect volume |
| `docker-compose down -v` | Remove volumes (⚠️ deletes data!) |

## Useful Docker Commands

| Command | Description |
|---------|-------------|
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker images` | List images |
| `docker stats` | Resource usage |
| `docker system prune` | Clean up unused resources |
| `docker system df` | Show disk usage |

## Debugging Workflow

1. **Check container status**: `docker-compose ps`
2. **Check health**: `curl http://localhost:616/health`
3. **Check logs**: `docker-compose logs -f web`
4. **Check database**: `docker-compose logs db`
5. **Access container**: `docker-compose exec web bash`
6. **Check environment**: `docker-compose exec web env | grep DB_`
7. **Restart**: `docker-compose restart`

## Data Backup Strategy

```bash
# Daily backup
docker-compose exec -T db pg_dump -U postgres personalfinances > backup_$(date +%Y%m%d).sql

# Or use make
make backup  # Creates backups/backup_YYYYMMDD_HHMMSS.sql

# Restore
docker-compose exec -T db psql -U postgres personalfinances < backup_file.sql
# Or
make restore FILE=backups/backup_file.sql
```

## Port Mappings

| Container | Internal Port | External Port | Access |
|-----------|--------------|---------------|--------|
| Web (dev) | 5000 | 616 | http://localhost:616 |
| Web (prod) | 8000 | 8000 | http://localhost:8000 |
| Database (dev) | 5432 | 5432 | localhost:5432 |
| Database (prod) | 5432 | (internal only) | Not exposed |

## Container Names

| Service | Container Name |
|---------|----------------|
| Development Web | finances_web |
| Development DB | finances_db |
| Production Web | finances_web_prod |
| Production DB | finances_db_prod |

## Documentation Quick Links

- **Start Here**: [START-HERE.md](START-HERE.md) ⭐
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Docker Setup**: [DOCKER-SETUP.md](DOCKER-SETUP.md)
- **Full Docs**: [README.docker.md](README.docker.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Overview**: [SETUP-SUMMARY.md](SETUP-SUMMARY.md)

## Pro Tips 💡

1. Use `make` commands for faster workflow
2. Check health endpoint regularly
3. Backup before major changes
4. Use `docker-compose logs -f web` to watch logs
5. Database data persists across restarts
6. Code changes auto-reload in dev mode
7. Use `--tail=N` to limit log output

## Emergency Commands

```bash
# Nuclear option - complete reset (⚠️ DELETES ALL DATA)
docker-compose down -v
docker system prune -a
docker-compose up -d --build

# Force recreate containers
docker-compose up -d --force-recreate

# Remove everything Docker-related (⚠️ CAREFUL)
docker system prune -a --volumes
```

---

**Print this page for quick reference! 📋**

For detailed explanations, see [START-HERE.md](START-HERE.md)
