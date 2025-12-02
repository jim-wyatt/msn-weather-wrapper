#!/bin/bash
#
# Developer Environment Manager for MSN Weather Wrapper
# This script sets up a complete containerized development environment using Podman
#
# Usage: ./dev.sh [command]
# Commands:
#   setup     - Initial setup (build images, install dependencies)
#   start     - Start all development containers
#   stop      - Stop all containers
#   restart   - Restart all containers
#   clean     - Remove all containers, images, and volumes
#   test      - Run all tests (backend + frontend)
#   logs      - Show logs from all containers
#   shell-api - Open shell in API container
#   shell-frontend - Open shell in frontend container
#   rebuild   - Rebuild all containers from scratch

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="msn-weather-wrapper"
COMPOSE_FILE="podman-compose.dev.yml"

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_podman() {
    if ! command -v podman &> /dev/null; then
        log_error "Podman is not installed. Please install it first."
        echo "  Ubuntu/Debian: sudo apt-get install podman"
        echo "  Fedora: sudo dnf install podman"
        echo "  macOS: brew install podman"
        exit 1
    fi
    log_success "Podman is installed ($(podman --version))"
}

check_podman_compose() {
    if ! command -v podman-compose &> /dev/null; then
        log_warning "podman-compose is not installed. Installing..."
        pip3 install --user podman-compose
        log_success "podman-compose installed"
    else
        log_success "podman-compose is installed ($(podman-compose --version))"
    fi
}

setup_dev_env() {
    log_info "Setting up development environment..."
    
    # Check prerequisites
    check_podman
    check_podman_compose
    
    # Create development docker-compose file if it doesn't exist
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_info "Creating development compose file..."
        create_dev_compose
    fi
    
    # Build images
    log_info "Building container images..."
    podman-compose -f "$COMPOSE_FILE" build
    
    log_success "Development environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "  ./dev.sh start    - Start the development environment"
    echo "  ./dev.sh logs     - View logs"
    echo "  ./dev.sh test     - Run tests"
}

start_dev() {
    log_info "Starting development containers..."
    podman-compose -f "$COMPOSE_FILE" up -d
    
    log_success "Containers started!"
    echo ""
    echo "Services available at:"
    echo "  Frontend:  http://localhost:5173"
    echo "  API:       http://localhost:5000"
    echo "  Health:    http://localhost:5000/api/v1/health/ready"
    echo ""
    echo "View logs with: ./dev.sh logs"
}

stop_dev() {
    log_info "Stopping development containers..."
    podman-compose -f "$COMPOSE_FILE" down
    log_success "Containers stopped"
}

restart_dev() {
    log_info "Restarting development containers..."
    stop_dev
    start_dev
}

clean_dev() {
    log_warning "This will remove all containers, images, and volumes!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        podman-compose -f "$COMPOSE_FILE" down -v
        podman rmi $(podman images | grep $PROJECT_NAME | awk '{print $3}') 2>/dev/null || true
        log_success "Cleanup complete"
    else
        log_info "Cleanup cancelled"
    fi
}

run_tests() {
    log_info "Running backend tests..."
    podman-compose -f "$COMPOSE_FILE" exec api pytest -v
    
    log_info "Running frontend E2E tests..."
    podman-compose -f "$COMPOSE_FILE" exec frontend npm run test:e2e
    
    log_success "All tests completed!"
}

generate_and_serve_docs() {
    log_info "Generating comprehensive documentation with reports..."
    
    # Check if mkdocs is installed
    if ! command -v mkdocs &> /dev/null; then
        log_warning "mkdocs not found. Installing..."
        pip3 install --user mkdocs mkdocs-material pymdown-extensions
    fi
    
    # Create reports directory
    mkdir -p docs/reports
    
    # Run backend tests with coverage and generate reports
    log_info "Running backend tests with coverage..."
    podman-compose -f "$COMPOSE_FILE" exec -T api pytest \
        --cov=msn_weather_wrapper \
        --cov-report=html:htmlcov \
        --cov-report=json:coverage.json \
        --cov-report=term \
        --junitxml=junit.xml \
        -v || true
    
    # Copy coverage reports from container
    log_info "Extracting coverage data..."
    podman cp msn-weather-api-dev:/app/coverage.json ./coverage.json 2>/dev/null || true
    podman cp msn-weather-api-dev:/app/htmlcov ./htmlcov 2>/dev/null || true
    podman cp msn-weather-api-dev:/app/junit.xml ./junit.xml 2>/dev/null || true
    
    # Generate coverage report
    if [ -f coverage.json ]; then
        log_info "Generating coverage report..."
        python3 tools/generate_reports.py --type coverage --input . --output docs/reports/coverage-report.md
    fi
    
    # Generate test report
    if [ -f junit.xml ]; then
        log_info "Generating test report..."
        mkdir -p test-results
        mv junit.xml test-results/
        python3 tools/generate_reports.py --type test --input test-results --output docs/reports/test-report.md
    fi
    
    # Run security scan
    log_info "Running security scan..."
    podman-compose -f "$COMPOSE_FILE" exec -T api bash -c \
        "pip install bandit safety && bandit -r src/ -f json -o bandit-report.json || true" || true
    
    # Copy security report from container
    podman cp msn-weather-api-dev:/app/bandit-report.json ./bandit-report.json 2>/dev/null || true
    
    if [ -f bandit-report.json ]; then
        log_info "Generating security report..."
        mkdir -p security-results
        mv bandit-report.json security-results/
        python3 tools/generate_reports.py --type security --input security-results --output docs/reports/security-report.md
    fi
    
    # Generate license report
    log_info "Generating license report..."
    podman-compose -f "$COMPOSE_FILE" exec -T api bash -c \
        "pip install pip-licenses && pip-licenses --format=json --output-file=licenses.json" || true
    
    # Copy license report from container
    podman cp msn-weather-api-dev:/app/licenses.json ./licenses.json 2>/dev/null || true
    
    if [ -f licenses.json ]; then
        mkdir -p license-results
        mv licenses.json license-results/
        python3 tools/generate_reports.py --type license --input license-results --output docs/reports/license-report.md
    fi
    
    # Generate CI/CD report
    log_info "Generating CI/CD pipeline report..."
    python3 tools/generate_reports.py --type cicd --output docs/reports/ci-cd.md
    
    # Create reports index if it doesn't exist
    if [ ! -f docs/reports/index.md ]; then
        cat > docs/reports/index.md << 'INDEXEOF'
# Reports Overview

Automated reports generated from test execution, code coverage, security scans, and license compliance checks.

## 📊 Available Reports

- **[Test Report](test-report.md)** - Test execution results and statistics
- **[Coverage Report](coverage-report.md)** - Code coverage analysis
- **[Security Report](security-report.md)** - Security vulnerability scan results
- **[License Report](license-report.md)** - Dependency license compliance
- **[CI/CD Pipeline](ci-cd.md)** - Pipeline execution status

## 🔄 Report Generation

Reports are automatically generated during CI/CD pipeline execution and can be regenerated locally using:

```bash
./dev.sh docs
```

All reports are timestamped and reflect the current state of the codebase.
INDEXEOF
        log_success "Created reports index"
    fi
    
    # Update README in reports
    if [ ! -f docs/reports/README.md ]; then
        ln -sf index.md docs/reports/README.md
    fi
    
    log_success "All reports generated!"
    
    # Start MkDocs server
    log_info "Starting documentation server..."
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📚 Documentation site will be available at:"
    echo "   http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    mkdocs serve
}

show_logs() {
    podman-compose -f "$COMPOSE_FILE" logs -f
}

shell_api() {
    log_info "Opening shell in API container..."
    podman-compose -f "$COMPOSE_FILE" exec api /bin/bash
}

shell_frontend() {
    log_info "Opening shell in frontend container..."
    podman-compose -f "$COMPOSE_FILE" exec frontend /bin/sh
}

rebuild_all() {
    log_info "Rebuilding all containers..."
    podman-compose -f "$COMPOSE_FILE" down
    podman-compose -f "$COMPOSE_FILE" build --no-cache
    log_success "Rebuild complete!"
}

create_dev_compose() {
    cat > "$COMPOSE_FILE" << 'EOF'
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Containerfile.dev
    container_name: msn-weather-api-dev
    ports:
      - "5000:5000"
    volumes:
      - ./src:/app/src:z
      - ./api.py:/app/api.py:z
      - ./tests:/app/tests:z
      - ./pyproject.toml:/app/pyproject.toml:z
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - PYTHONUNBUFFERED=1
    command: python api.py
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/v1/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  frontend:
    build:
      context: ./frontend
      dockerfile: Containerfile.dev
    container_name: msn-weather-frontend-dev
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src:z
      - ./frontend/tests:/app/tests:z
      - ./frontend/public:/app/public:z
    environment:
      - NODE_ENV=development
    command: npm run dev -- --host 0.0.0.0
    depends_on:
      - api

  test-runner:
    build:
      context: .
      dockerfile: Containerfile.dev
    container_name: msn-weather-test-runner
    volumes:
      - ./src:/app/src:z
      - ./api.py:/app/api.py:z
      - ./tests:/app/tests:z
      - ./pyproject.toml:/app/pyproject.toml:z
    environment:
      - PYTHONUNBUFFERED=1
    command: pytest --cov=msn_weather_wrapper --cov-report=term-missing --cov-report=html
    profiles:
      - test
EOF
    log_success "Development compose file created: $COMPOSE_FILE"
}

show_usage() {
    cat << EOF
Developer Environment Manager for MSN Weather Wrapper

Usage: ./dev.sh [command]

Commands:
  setup             Initial setup (build images, install dependencies)
  start             Start all development containers
  stop              Stop all containers
  restart           Restart all containers
  clean             Remove all containers, images, and volumes
  test              Run all tests (backend + frontend)
  docs              Generate all reports and serve documentation site
  logs              Show logs from all containers
  shell-api         Open shell in API container
  shell-frontend    Open shell in frontend container
  rebuild           Rebuild all containers from scratch
  help              Show this help message

Examples:
  ./dev.sh setup        # First-time setup
  ./dev.sh start        # Start development
  ./dev.sh logs         # Watch logs
  ./dev.sh test         # Run tests
  ./dev.sh docs         # Generate reports & serve docs

EOF
}

# Main script logic
case "${1:-help}" in
    setup)
        setup_dev_env
        ;;
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    restart)
        restart_dev
        ;;
    clean)
        clean_dev
        ;;
    test)
        run_tests
        ;;
    docs)
        generate_and_serve_docs
        ;;
    logs)
        show_logs
        ;;
    shell-api)
        shell_api
        ;;
    shell-frontend)
        shell_frontend
        ;;
    rebuild)
        rebuild_all
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
