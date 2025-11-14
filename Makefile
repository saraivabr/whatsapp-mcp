# ==============================================
# WhatsApp MCP - Makefile
# Quick commands for Docker management
# ==============================================

.PHONY: help start stop restart logs status build clean dev prod

# Default target
.DEFAULT_GOAL := help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)╔════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║   WhatsApp MCP - Available Commands    ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

start: ## Start all services
	@echo "$(BLUE)Starting WhatsApp MCP services...$(NC)"
	@./start.sh

stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	@./stop.sh

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

logs: ## View logs from all services
	@./logs.sh

status: ## Check status of all services
	@./status.sh

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker-compose build --no-cache
	@echo "$(GREEN)✓ Build complete$(NC)"

rebuild: ## Rebuild and restart all services
	@echo "$(BLUE)Rebuilding and restarting...$(NC)"
	@docker-compose up --build -d
	@echo "$(GREEN)✓ Services rebuilt and started$(NC)"

clean: ## Stop services and remove volumes
	@echo "$(YELLOW)⚠ This will remove all data!$(NC)"
	@docker-compose down -v
	@echo "$(GREEN)✓ Cleaned up$(NC)"

dev: ## Start in development mode
	@echo "$(BLUE)Starting in development mode...$(NC)"
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

prod: ## Start in production mode
	@echo "$(BLUE)Starting in production mode...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Production services started$(NC)"

shell-bridge: ## Open shell in Go bridge container
	@docker exec -it whatsapp-bridge sh

shell-backend: ## Open shell in backend container
	@docker exec -it whatsapp-backend sh

shell-frontend: ## Open shell in frontend container
	@docker exec -it whatsapp-frontend sh

logs-bridge: ## View Go bridge logs
	@docker-compose logs -f --tail=100 whatsapp-bridge

logs-backend: ## View backend logs
	@docker-compose logs -f --tail=100 backend

logs-frontend: ## View frontend logs
	@docker-compose logs -f --tail=100 frontend

ps: ## List running containers
	@docker-compose ps

down: ## Stop all services without removing volumes
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

prune: ## Remove all unused Docker resources
	@echo "$(YELLOW)⚠ This will remove unused images, containers, and networks$(NC)"
	@docker system prune -af
	@echo "$(GREEN)✓ Docker resources pruned$(NC)"

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@docker inspect --format='{{.Name}}: {{.State.Health.Status}}' whatsapp-bridge whatsapp-backend whatsapp-frontend 2>/dev/null || echo "Some services not running"

update: ## Pull latest changes and rebuild
	@echo "$(BLUE)Updating from git and rebuilding...$(NC)"
	@git pull
	@docker-compose up --build -d
	@echo "$(GREEN)✓ Updated and restarted$(NC)"
