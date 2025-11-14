#!/bin/bash

# ==============================================
# WhatsApp MCP - Startup Script
# ==============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   WhatsApp MCP - Web Interface        ║"
    echo "║   Complete Docker Environment          ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker found: $(docker --version)"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose found"

    # Check .env file
    if [ ! -f .env ]; then
        print_warning ".env file not found"
        print_info "Creating .env from .env.example..."

        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Please edit .env and add your ANTHROPIC_API_KEY"
            print_info "Opening .env file..."
            ${EDITOR:-nano} .env
        else
            print_error ".env.example not found. Cannot create .env file."
            exit 1
        fi
    fi

    # Check if ANTHROPIC_API_KEY is set
    source .env
    if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_api_key_here" ]; then
        print_error "ANTHROPIC_API_KEY is not set in .env file"
        print_info "Please set your Anthropic API key in .env file"
        exit 1
    fi
    print_success "Environment configured"
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    mkdir -p whatsapp-bridge/store
    print_success "Directories created"
}

# Start services
start_services() {
    print_info "Starting Docker services..."

    # Ask build or use cached
    read -p "Do you want to rebuild images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Building and starting services..."
        docker-compose up --build -d
    else
        print_info "Starting services with cached images..."
        docker-compose up -d
    fi

    print_success "Services started!"
}

# Show status
show_status() {
    echo ""
    print_info "Service Status:"
    docker-compose ps
}

# Show logs
show_instructions() {
    echo ""
    print_header
    print_success "All services are running!"
    echo ""
    print_info "Access points:"
    echo "  • Frontend:     http://localhost:3000"
    echo "  • Backend API:  http://localhost:8000"
    echo "  • Go Bridge:    http://localhost:8080"
    echo ""
    print_info "Useful commands:"
    echo "  • View logs:        docker-compose logs -f"
    echo "  • Stop services:    docker-compose down"
    echo "  • Restart:          docker-compose restart"
    echo "  • View status:      docker-compose ps"
    echo ""
    print_warning "First time setup:"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Scan the QR code with WhatsApp"
    echo "  3. Wait for connection to establish"
    echo "  4. Start chatting with your AI assistant!"
    echo ""
}

# Main
main() {
    print_header
    check_prerequisites
    create_directories
    start_services
    show_status
    show_instructions
}

main
