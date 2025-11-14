#!/bin/bash

# ==============================================
# WhatsApp MCP - Logs Viewer Script
# ==============================================

set -e

# Colors
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   WhatsApp MCP - Service Logs          ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check if a service name was provided
if [ -n "$1" ]; then
    echo "Showing logs for: $1"
    echo "Press Ctrl+C to exit"
    echo ""
    docker-compose logs -f --tail=100 "$1"
else
    echo "Available services:"
    echo "  1. whatsapp-bridge  - Go WhatsApp connection"
    echo "  2. backend          - Python FastAPI server"
    echo "  3. frontend         - Next.js web interface"
    echo "  4. all              - All services"
    echo ""
    read -p "Choose service (1-4) or enter name: " choice

    case $choice in
        1)
            docker-compose logs -f --tail=100 whatsapp-bridge
            ;;
        2)
            docker-compose logs -f --tail=100 backend
            ;;
        3)
            docker-compose logs -f --tail=100 frontend
            ;;
        4|all)
            docker-compose logs -f --tail=100
            ;;
        *)
            docker-compose logs -f --tail=100 "$choice"
            ;;
    esac
fi
