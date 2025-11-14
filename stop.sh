#!/bin/bash

# ==============================================
# WhatsApp MCP - Stop Script
# ==============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   Stopping WhatsApp MCP Services       ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Ask if user wants to remove volumes
read -p "Do you want to remove data volumes? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Stopping services and removing volumes..."
    docker-compose down -v
    print_success "Services stopped and volumes removed"
else
    print_info "Stopping services (keeping data)..."
    docker-compose down
    print_success "Services stopped (data preserved)"
fi

print_info "All containers stopped"
