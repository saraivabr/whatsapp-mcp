#!/bin/bash

# ==============================================
# WhatsApp MCP - Status Script
# ==============================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   WhatsApp MCP - System Status         ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_service() {
    local service=$1
    local port=$2

    if docker-compose ps | grep -q "$service.*Up"; then
        if curl -sf "http://localhost:$port" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $service${NC} - Running and healthy (port $port)"
        else
            echo -e "${YELLOW}⚠ $service${NC} - Running but not responding (port $port)"
        fi
    else
        echo -e "${RED}✗ $service${NC} - Not running"
    fi
}

print_header

echo "Docker Services:"
echo "─────────────────────────────────────────"
docker-compose ps
echo ""

echo "Health Status:"
echo "─────────────────────────────────────────"
check_service "whatsapp-bridge" "8080"
check_service "backend" "8000"
check_service "frontend" "3000"
echo ""

echo "Docker Resources:"
echo "─────────────────────────────────────────"
docker stats --no-stream whatsapp-bridge whatsapp-backend whatsapp-frontend 2>/dev/null || echo "Services not running"
echo ""

echo "Access URLs:"
echo "─────────────────────────────────────────"
echo -e "${BLUE}Frontend:${NC}    http://localhost:3000"
echo -e "${BLUE}Backend:${NC}     http://localhost:8000"
echo -e "${BLUE}Go Bridge:${NC}   http://localhost:8080"
echo ""

echo "Quick Actions:"
echo "─────────────────────────────────────────"
echo "  View logs:         ./logs.sh"
echo "  Stop services:     ./stop.sh"
echo "  Restart services:  docker-compose restart"
