.PHONY: help build up down restart logs shell db-shell migrate backup clean dev prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Running migrations..."
	docker-compose exec -T web flask db upgrade
	@echo ""
	@echo "✅ Application is running at http://localhost:616"

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs (use ctrl+c to exit)
	docker-compose logs -f

logs-web: ## View web service logs only
	docker-compose logs -f web

logs-db: ## View database logs only
	docker-compose logs -f db

shell: ## Access web container shell
	docker-compose exec web bash

db-shell: ## Access PostgreSQL shell
	docker-compose exec db psql -U postgres -d personalfinances

migrate: ## Run database migrations
	docker-compose exec web flask db upgrade

migrate-create: ## Create a new migration (use: make migrate-create MSG="migration message")
	docker-compose exec web flask db migrate -m "$(MSG)"

backup: ## Backup database
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U postgres personalfinances > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backups/ directory"

restore: ## Restore database from backup (use: make restore FILE=backups/backup.sql)
	docker-compose exec -T db psql -U postgres personalfinances < $(FILE)
	@echo "Database restored from $(FILE)"

clean: ## Stop and remove all containers, volumes, and images
	docker-compose down -v
	docker-compose rm -f
	@echo "Cleaned up Docker resources"

dev: up ## Start development environment (alias for up)

prod: ## Start production environment
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Running migrations..."
	docker-compose -f docker-compose.prod.yml exec -T web flask db upgrade
	@echo ""
	@echo "✅ Production application is running at http://localhost:8000"

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## View production logs
	docker-compose -f docker-compose.prod.yml logs -f

status: ## Show container status
	docker-compose ps

rebuild: ## Rebuild and restart all services
	docker-compose down
	docker-compose up -d --build
	@echo "Waiting for services to be ready..."
	@sleep 5
	docker-compose exec -T web flask db upgrade
	@echo ""
	@echo "✅ Application rebuilt and running at http://localhost:616"
