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
#   monitor   - DevSecOps dashboard with RAG status (Local env + GitHub workflows)

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

    # Check for port conflicts
    if ! check_port_conflicts; then
        exit 1
    fi

    podman-compose -f "$COMPOSE_FILE" up -d

    log_success "Containers started!"
    echo ""
    echo "Services available at:"
    echo "  Frontend:  http://localhost:5173"
    echo "  API:       http://localhost:5000"
    echo "  Health:    http://localhost:5000/api/v1/health"
    echo ""
    echo "View logs with: ./dev.sh logs"
    echo "Check status with: ./dev.sh status"
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
    local clean_gitignore=false

    # Parse arguments
    if [[ "${1:-}" == "--gitignore" ]] || [[ "${1:-}" == "-g" ]]; then
        clean_gitignore=true
    fi

    if [ "$clean_gitignore" = true ]; then
        log_warning "This will remove all files matching patterns in .gitignore!"
        echo "Files to be removed:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        git clean -ndX | sed 's/^Would remove /  - /'
        echo ""
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Removing gitignored files..."
            git clean -fdX
            log_success "Gitignored files removed"
        else
            log_info "Cleanup cancelled"
        fi
    else
        log_warning "This will remove all containers, images, and volumes!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cleaning up containers..."
            podman-compose -f "$COMPOSE_FILE" down -v
            podman rmi $(podman images | grep $PROJECT_NAME | awk '{print $3}') 2>/dev/null || true
            log_success "Container cleanup complete"

            # Ask about gitignored files
            echo ""
            log_info "Would you also like to remove gitignored files?"
            read -p "Remove gitignored files? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "Files to be removed:"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                git clean -ndX | sed 's/^Would remove /  - /'
                echo ""
                read -p "Proceed with removal? (y/N) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    log_info "Removing gitignored files..."
                    git clean -fdX
                    log_success "Gitignored files removed"
                else
                    log_info "Gitignore cleanup skipped"
                fi
            else
                log_info "Gitignore cleanup skipped"
            fi
        else
            log_info "Cleanup cancelled"
        fi
    fi
}

show_status() {
    log_info "Checking container status..."
    echo ""

    # Check if containers exist
    if ! podman ps -a | grep -q "msn-weather"; then
        log_warning "No containers found. Run './dev.sh setup' first."
        return
    fi

    # Show container status
    echo "Container Status:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    podman ps -a --filter "name=msn-weather" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""

    # Check service health
    if podman ps | grep -q "msn-weather-api-dev"; then
        echo "Service Health:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        if curl -s http://localhost:5000/api/v1/health > /dev/null 2>&1; then
            log_success "API:       http://localhost:5000 - HEALTHY"
        else
            log_warning "API:       http://localhost:5000 - NOT RESPONDING"
        fi

        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            log_success "Frontend:  http://localhost:5173 - HEALTHY"
        else
            log_warning "Frontend:  http://localhost:5173 - NOT RESPONDING"
        fi
    else
        log_info "Containers are not running. Start with: ./dev.sh start"
    fi
    echo ""
}

check_port_conflicts() {
    log_info "Checking for port conflicts..."
    local conflicts=0

    # Check port 5000 (API)
    if netstat -tuln 2>/dev/null | grep -q ":5000 " || ss -tuln 2>/dev/null | grep -q ":5000 "; then
        log_error "Port 5000 is already in use (required for API)"
        conflicts=$((conflicts + 1))
    fi

    # Check port 5173 (Frontend)
    if netstat -tuln 2>/dev/null | grep -q ":5173 " || ss -tuln 2>/dev/null | grep -q ":5173 "; then
        log_error "Port 5173 is already in use (required for Frontend)"
        conflicts=$((conflicts + 1))
    fi

    if [ $conflicts -gt 0 ]; then
        log_error "Found $conflicts port conflict(s). Please free the ports before starting."
        echo "  Tip: Use 'lsof -i :5000' or 'lsof -i :5173' to find the process using these ports"
        return 1
    fi

    log_success "No port conflicts detected"
    return 0
}

run_tests() {
    local watch_mode=false

    # Parse arguments
    if [[ "${1:-}" == "--watch" ]] || [[ "${1:-}" == "-w" ]]; then
        watch_mode=true
    fi

    # Check if containers are running
    if ! podman ps | grep -q "msn-weather-api-dev"; then
        log_error "Containers are not running. Start them with: ./dev.sh start"
        exit 1
    fi

    if [ "$watch_mode" = true ]; then
        log_info "Running tests in watch mode (Ctrl+C to stop)..."
        echo ""
        podman exec -it msn-weather-api-dev pytest -v --looponfail
        clear
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        local commit=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        local workflows_json=$(get_github_workflows)

        # Compact header (fits 80x24)
        printf "${BLUE}%s${NC}\n" "$(printf '=%.0s' {1..70})"
        printf " ${YELLOW}⚡ DevSecOps${NC} • ${CYAN}${GITHUB_OWNER}/${GITHUB_REPO}${NC} • ${BLUE}${timestamp}${NC}\n"
        printf " ${BLUE}Branch${NC} ${MAGENTA}${branch}${NC} @ ${commit}  •  Auto-refresh:60s  •  Ctrl+C to exit\n"
        printf "${BLUE}%s${NC}\n" "$(printf '-%.0s' {1..70})"

        # Local
        local cont_status=$(get_local_status containers)
        local cont_rag=$(get_rag_status "$cont_status")
        local pyenv_status=$(get_local_status python_env)
        local git_status=$(get_local_status git)
        printf " ${YELLOW}Local${NC}  "
        format_rag "$cont_rag"; printf " Cntnr "
        case "$cont_status" in
            healthy) printf "${GREEN}OK${NC}" ;;
            partial) printf "${YELLOW}Partial${NC}" ;;
            unhealthy) printf "${YELLOW}Unhealthy${NC}" ;;
            stopped) printf "${BLUE}Stopped${NC}" ;;
            *) printf "${BLUE}NA${NC}" ;;
        esac
        printf "  PyEnv "
        case "$pyenv_status" in
            active) printf "${GREEN}active${NC}" ;;
            inactive) printf "${YELLOW}exists${NC}" ;;
            none) printf "${BLUE}none${NC}" ;;
        esac
        printf "  Git "
        case "${git_status%%|*}" in
            clean) printf "${GREEN}clean${NC}\n" ;;
            dirty)
                IFS='+' read -r staged unstaged untracked <<< "${git_status##*|}"
                printf "${YELLOW}%s/%s/%s${NC}\n" "$staged" "$unstaged" "$untracked" ;;
        esac

        # Quality
        local test_status=$(get_local_status tests)
        local test_rag=$(get_rag_status "$test_status")
        local cov_status=$(get_local_status coverage)
        printf " ${YELLOW}Quality${NC} "
        format_rag "$test_rag"; printf " Tests "
        case "$test_status" in
            pass) printf "${GREEN}pass${NC}" ;;
            fail) printf "${RED}fail${NC}" ;;
            *) printf "${BLUE}none${NC}" ;;
        esac
        printf "  Cov "
        if [ "$cov_status" != "none" ] && [ "$cov_status" != "unknown" ]; then
            local cov_rag=$(get_rag_status "" "$cov_status")
            format_rag "$cov_rag"; printf " %s%%" "$cov_status"
        else
            printf "${BLUE}○${NC} --"
        fi
        printf "  mypy "
        if command -v mypy &> /dev/null && [ -f "pyproject.toml" ]; then printf "${GREEN}yes${NC}"; else printf "${BLUE}no${NC}"; fi
        printf "  ruff "
        if command -v ruff &> "/dev/null" || (command -v pip &> /dev/null && pip list 2>/dev/null | grep -q "ruff"); then printf "${GREEN}yes${NC}\n"; else printf "${BLUE}no${NC}\n"; fi

        # Security
        local sec_status=$(get_local_status security)
        local sec_rag=$(get_rag_status "${sec_status%%|*}")
        local dep_status=$(get_local_status dependencies)
        local dep_rag=$(get_rag_status "${dep_status%%|*}")
        printf " ${YELLOW}Security${NC} "
        format_rag "$sec_rag"; printf " SAST "
        case "${sec_status%%|*}" in pass) printf "${GREEN}ok${NC}";; fail) printf "${RED}${sec_status##*|} issues${NC}";; *) printf "${BLUE}none${NC}";; esac
        printf "  "
        format_rag "$dep_rag"; printf " Deps "
        case "${dep_status%%|*}" in pass) printf "${GREEN}clean${NC}";; warn) printf "${YELLOW}${dep_status##*|} vulns${NC}";; unchecked) printf "${BLUE}n/a${NC}";; *) printf "${BLUE}n/a${NC}";; esac
        printf "  Lic "
        if [ -f "artifacts/security-reports/licenses.json" ]; then local pkgs=$(jq 'length' artifacts/security-reports/licenses.json 2>/dev/null); format_rag "GREEN|✅"; printf " %s" "$pkgs"; else format_rag "GREY|○"; printf " --"; fi
        printf "  SBOM "
        local sbom_count=$(find sbom_output -name "*.json" 2>/dev/null | wc -l || echo "0")
        if [ "$sbom_count" -gt 0 ]; then format_rag "GREEN|✅"; printf " %s\n" "$sbom_count"; else format_rag "GREY|○"; printf " --\n"; fi

        # GitHub
        printf " ${YELLOW}CI/CD${NC}  "
        local ci_status=$(get_workflow_status "CI/CD Pipeline" "$workflows_json")
        format_rag "$(get_rag_status "$ci_status")"; printf " CI "
        case "$ci_status" in success) printf "${GREEN}ok${NC}";; failure) printf "${RED}fail${NC}";; cancelled) printf "${BLUE}cancel${NC}";; *) printf "${BLUE}n/a${NC}";; esac
        printf "  Sec "
        local sec_wf_status=$(get_workflow_status "Security" "$workflows_json")
        format_rag "$(get_rag_status "$sec_wf_status")"; case "$sec_wf_status" in success) printf "${GREEN}ok${NC}";; failure) printf "${RED}fail${NC}";; cancelled) printf "${BLUE}cancel${NC}";; *) printf "${BLUE}n/a${NC}";; esac
        printf "  AutoVer "
        local version_status=$(get_workflow_status "Auto Version and Release" "$workflows_json")
        format_rag "$(get_rag_status "$version_status")"; case "$version_status" in success) printf "${GREEN}ok${NC}";; failure) printf "${RED}fail${NC}";; cancelled) printf "${BLUE}cancel${NC}";; *) printf "${BLUE}n/a${NC}";; esac
        printf "  Perf "
        local perf_status=$(get_workflow_status "Performance Testing" "$workflows_json")
        format_rag "$(get_rag_status "$perf_status")"; case "$perf_status" in success) printf "${GREEN}ok${NC}\n";; failure) printf "${RED}fail${NC}\n";; cancelled) printf "${BLUE}cancel${NC}\n";; *) printf "${BLUE}n/a${NC}\n";; esac

        printf "${BLUE}%s${NC}\n" "$(printf '=%.0s' {1..70})"
                    return
                fi

                local api_up=$(podman ps --filter "name=msn-weather-api-dev" --format "{{.Status}}" 2>/dev/null)
                local fe_up=$(podman ps --filter "name=msn-weather-frontend-dev" --format "{{.Status}}" 2>/dev/null)

                if [ -n "$api_up" ] && [ -n "$fe_up" ]; then
                    # Check API health
                    if curl -s -f --max-time 2 http://localhost:5000/api/v1/health > /dev/null 2>&1; then
                        echo "healthy"
                    else
                        echo "unhealthy"
                    fi
                elif [ -n "$api_up" ] || [ -n "$fe_up" ]; then
                    echo "partial"
                else
                    echo "stopped"
                fi
                ;;
            git)
                local staged=$(git diff --cached --numstat 2>/dev/null | wc -l || echo "0")
                local unstaged=$(git diff --numstat 2>/dev/null | wc -l || echo "0")
                local untracked=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l || echo "0")

                if [ "$staged" -gt 0 ] || [ "$unstaged" -gt 0 ] || [ "$untracked" -gt 0 ]; then
                    echo "dirty|$staged+$unstaged+$untracked"
                else
                    echo "clean"
                fi
                ;;
            python_env)
                if [ -d "venv" ]; then
                    if [ -n "$VIRTUAL_ENV" ]; then
                        echo "active"
                    else
                        echo "inactive"
                    fi
                else
                    echo "none"
                fi
                ;;
            dependencies)
                if [ -f "pyproject.toml" ] && command -v pip &> /dev/null; then
                    # Check if pip-audit is available
                    if command -v pip-audit &> /dev/null 2>&1 || pip list 2>/dev/null | grep -q "pip-audit"; then
                        local vuln_count=$(pip-audit --desc on --format json 2>/dev/null | jq '.dependencies | length' 2>/dev/null || echo "0")
                        if [ "${vuln_count:-0}" -eq 0 ] 2>/dev/null; then
                            echo "pass"
                        else
                            echo "warn|$vuln_count"
                        fi
                    else
                        echo "unchecked"
                    fi
                else
                    echo "none"
                fi
                ;;
            *)
                echo "unknown"
                ;;
        esac
    }

    # Function to fetch GitHub workflow status
    get_github_workflows() {
        local cache_file="/tmp/gh_workflows_${GITHUB_OWNER}_${GITHUB_REPO}.json"
        local cache_age=0

        # Check cache age (refresh every 30 seconds)
        if [ -f "$cache_file" ]; then
            cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || echo "0")))
        fi

        # Fetch if cache is old or doesn't exist
        if [ ! -f "$cache_file" ] || [ "$cache_age" -gt 30 ]; then
            curl -s --max-time 5 \
                "${GITHUB_API_BASE}/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs?per_page=5&status=completed" \
                > "$cache_file" 2>/dev/null || echo '{"workflow_runs":[]}' > "$cache_file"
        fi

        cat "$cache_file"
    }

    # Function to get latest workflow run status for a specific workflow
    get_workflow_status() {
        local workflow_name="$1"
        local workflows_json="$2"

        # Extract the latest run for this workflow
        local status=$(echo "$workflows_json" | jq -r --arg name "$workflow_name" \
            '.workflow_runs[] | select(.name == $name) | .conclusion' 2>/dev/null | head -1)

        if [ -z "$status" ] || [ "$status" = "null" ]; then
            echo "unknown"
        else
            echo "$status"
        fi
    }

    # Function to draw the monitor display
    draw_monitor() {
        clear
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || \
            echo "unknown")
        local commit=$(git rev-parse --short HEAD 2>/dev/null || \
            echo "unknown")

        # Fetch GitHub workflow data
        local workflows_json=$(get_github_workflows)

        # Header
        echo ""
        printf "${BLUE}%s${NC}\n" "$(printf '=%.0s' {1..75})"
        printf "  ${YELLOW}⚡ DevSecOps Dashboard${NC}  ${BLUE}•${NC}  "
        printf "${CYAN}${GITHUB_OWNER}/${GITHUB_REPO}${NC}\n"
        printf "  ${BLUE}${timestamp}${NC}  ${BLUE}•${NC}  "
        printf "Auto-refresh: 60s  ${BLUE}•${NC}  "
        printf "Press ${GREEN}Ctrl+C${NC} to exit\n"
        printf "${BLUE}%s${NC}\n" "$(printf '=%.0s' {1..75})"
        echo ""
        printf "  ${MAGENTA}${branch}${NC} @ ${commit}\n"
        echo ""

        # LOCAL ENVIRONMENT
        printf "${YELLOW}🔧 Local Environment${NC}\n"

        # Container Services
        local cont_status=$(get_local_status containers)
        local cont_rag=$(get_rag_status "$cont_status")
        printf "  "
        format_rag "$cont_rag"
        printf " Containers: "
        case "$cont_status" in
            healthy) printf "${GREEN}Both services running & healthy${NC}" ;;
            partial) printf "${YELLOW}Partial (1 service down)${NC}" ;;
            unhealthy) printf "${YELLOW}Running but unhealthy${NC}" ;;
            stopped) printf "${BLUE}Services stopped${NC}" ;;
            disabled) printf "${BLUE}Podman not available${NC}" ;;
        esac
        echo ""

        # Python Virtual Environment
        local pyenv_status=$(get_local_status python_env)
        printf "  "
        case "$pyenv_status" in
            active) printf "${GREEN}✅${NC} Python Env: ${GREEN}venv/ active${NC}" ;;
            inactive) printf "${YELLOW}⚠️${NC} Python Env: ${YELLOW}venv/ exists but not activated${NC}" ;;
            none) printf "${BLUE}○${NC} Python Env: ${BLUE}Not configured${NC}" ;;
        esac
        echo ""

        # Git Working Directory
        local git_status=$(get_local_status git)
        local git_rag=$(get_rag_status "${git_status%%|*}")
        printf "  "
        format_rag "$git_rag"
        printf " Git Status: "
        case "${git_status%%|*}" in
            clean) printf "${GREEN}Clean (no uncommitted changes)${NC}" ;;
            dirty)
                local changes="${git_status##*|}"
                IFS='+' read -r staged unstaged untracked <<< "$changes"
                printf "${YELLOW}${staged} staged, ${unstaged} unstaged, "
                printf "${untracked} untracked${NC}" ;;
        esac
        echo ""

        # Pre-commit hooks
        if [ -f ".pre-commit-config.yaml" ]; then
            if [ -d ".git/hooks" ] && [ -f ".git/hooks/pre-commit" ]; then
                printf "  ${GREEN}✅${NC} Pre-commit: "
                printf "${GREEN}Installed & active${NC}\n"
            else
                printf "  ${YELLOW}⚠️${NC} Pre-commit: "
                printf "${YELLOW}Config exists but not installed${NC}\n"
            fi
        else
            printf "  ${BLUE}○${NC} Pre-commit: ${BLUE}Not configured${NC}\n"
        fi

        echo ""

        printf "${YELLOW}🧪 Code Quality & Testing${NC}\n"

        # Test Results
        local test_status=$(get_local_status tests)
        local test_rag=$(get_rag_status "$test_status")
        printf "  "
        format_rag "$test_rag"
        printf " Tests: "
        if [ "$test_status" = "pass" ]; then
            if [ -f "junit.xml" ]; then
                local tot=$(grep -oP 'tests="\K[0-9]+' junit.xml \
                    2>/dev/null | head -1)
                printf "${GREEN}%d tests passed${NC}" "${tot:-0}"
            else
                printf "${GREEN}All tests passed${NC}"
            fi
        elif [ "$test_status" = "fail" ]; then
            if [ -f "junit.xml" ]; then
                local tot=$(grep -oP 'tests="\K[0-9]+' junit.xml \
                    2>/dev/null | head -1)
                local fail=$(grep -oP 'failures="\K[0-9]+' junit.xml \
                    2>/dev/null | head -1)
                printf "${RED}%d/%d tests failed${NC}" "${fail:-0}" "${tot:-0}"
            else
                printf "${RED}Tests failed${NC}"
            fi
        else
            printf "${BLUE}No test report available${NC}"
        fi
        echo ""

        # Code Coverage
        local cov_status=$(get_local_status coverage)
        printf "  "
        if [ "$cov_status" != "none" ] && [ "$cov_status" != "unknown" ]; then
            local cov_rag=$(get_rag_status "" "$cov_status")
            format_rag "$cov_rag"
            printf " Coverage: "
            if [ "$cov_status" -ge 80 ]; then
                printf "${GREEN}%d%% (Excellent)${NC}" "$cov_status"
            elif [ "$cov_status" -ge 60 ]; then
                printf "${YELLOW}%d%% (Good)${NC}" "$cov_status"
            else
                printf "${RED}%d%% (Needs improvement)${NC}" "$cov_status"
            fi
        else
            printf "${BLUE}○${NC} Coverage: ${BLUE}No coverage report${NC}"
        fi
        echo ""

        # Type Checking & Linting
        if command -v mypy &> /dev/null && [ -f "pyproject.toml" ]; then
            printf "  ${GREEN}✅${NC} Type Check: ${GREEN}mypy available${NC}\n"
        else
            printf "  ${BLUE}○${NC} Type Check: "
            printf "${BLUE}mypy not installed${NC}\n"
        fi

        if command -v ruff &> /dev/null || \
           (command -v pip &> /dev/null && \
            pip list 2>/dev/null | grep -q "ruff"); then
            printf "  ${GREEN}✅${NC} Linter: ${GREEN}ruff available${NC}\n"
        else
            printf "  ${BLUE}○${NC} Linter: ${BLUE}ruff not installed${NC}\n"
        fi

        echo ""

        printf "${YELLOW}🔒 Security & Compliance${NC}\n"

        # SAST Security Scan
        local sec_status=$(get_local_status security)
        local sec_rag=$(get_rag_status "${sec_status%%|*}")
        printf "  "
        format_rag "$sec_rag"
        printf " SAST Scan: "
        if [ "${sec_status%%|*}" = "pass" ]; then
            printf "${GREEN}No critical vulnerabilities${NC}"
        elif [ "${sec_status%%|*}" = "fail" ]; then
            local issues="${sec_status##*|}"
            printf "${RED}%s critical issues found${NC}" "$issues"
        else
            printf "${BLUE}No security report${NC}"
        fi
        echo ""

        # Dependency Vulnerabilities
        local dep_status=$(get_local_status dependencies)
        local dep_rag=$(get_rag_status "${dep_status%%|*}")
        printf "  "
        format_rag "$dep_rag"
        printf " Dependencies: "
        case "${dep_status%%|*}" in
            pass) printf "${GREEN}No known vulnerabilities${NC}" ;;
            warn)
                local vuln_count="${dep_status##*|}"
                printf "${YELLOW}%s vulnerable packages${NC}" "$vuln_count" ;;
            unchecked) printf "${BLUE}Not scanned (pip-audit needed)${NC}" ;;
            none) printf "${BLUE}Unavailable${NC}" ;;
        esac
        echo ""

        # License Compliance
        printf "  "
        if [ -f "artifacts/security-reports/licenses.json" ]; then
            local pkgs=$(jq 'length' \
                "artifacts/security-reports/licenses.json" 2>/dev/null)
            format_rag "GREEN|✅"
            printf " Licenses: ${GREEN}%s dependencies tracked${NC}\n" "$pkgs"
        else
            format_rag "GREY|○"
            printf " Licenses: ${BLUE}No license report${NC}\n"
        fi

        # SBOM Generation
        local sbom_count=$(find sbom_output -name "*.json" 2>/dev/null | \
            wc -l || echo "0")
        printf "  "
        if [ "$sbom_count" -gt 0 ]; then
            format_rag "GREEN|✅"
            printf " SBOM: ${GREEN}%d SBOMs generated${NC}\n" "$sbom_count"
        else
            format_rag "GREY|○"
            printf " SBOM: ${BLUE}No SBOMs generated${NC}\n"
        fi

        echo ""

        printf "${YELLOW}🚀 GitHub CI/CD${NC} ${BLUE}(Latest Runs)${NC}\n"

        # CI/CD Pipeline
        local ci_status=$(get_workflow_status "CI/CD Pipeline" \
            "$workflows_json")
        local ci_rag=$(get_rag_status "$ci_status")
        printf "  "
        format_rag "$ci_rag"
        printf " CI/CD Pipeline: "
        case "$ci_status" in
            success) printf "${GREEN}Passed${NC}" ;;
            failure) printf "${RED}Failed${NC}" ;;
            cancelled) printf "${BLUE}Cancelled${NC}" ;;
            *) printf "${BLUE}No recent runs${NC}" ;;
        esac
        echo ""

        # Security Scans
        local sec_wf_status=$(get_workflow_status "Security" "$workflows_json")
        local sec_wf_rag=$(get_rag_status "$sec_wf_status")
        printf "  "
        format_rag "$sec_wf_rag"
        printf " Security Scans: "
        case "$sec_wf_status" in
            success) printf "${GREEN}Passed${NC}" ;;
            failure) printf "${RED}Failed${NC}" ;;
            cancelled) printf "${BLUE}Cancelled${NC}" ;;
            *) printf "${BLUE}No recent runs${NC}" ;;
        esac
        echo ""

        # Auto Version and Release
        local version_status=$(get_workflow_status \
            "Auto Version and Release" "$workflows_json")
        local version_rag=$(get_rag_status "$version_status")
        printf "  "
        format_rag "$version_rag"
        printf " Auto Version: "
        case "$version_status" in
            success) printf "${GREEN}Passed${NC}" ;;
            failure) printf "${RED}Failed${NC}" ;;
            cancelled) printf "${BLUE}Cancelled${NC}" ;;
            *) printf "${BLUE}No recent runs${NC}" ;;
        esac
        echo ""

        # Performance Tests
        local perf_status=$(get_workflow_status \
            "Performance Testing" "$workflows_json")
        local perf_rag=$(get_rag_status "$perf_status")
        printf "  "
        format_rag "$perf_rag"
        printf " Performance: "
        case "$perf_status" in
            success) printf "${GREEN}Passed${NC}" ;;
            failure) printf "${RED}Failed${NC}" ;;
            cancelled) printf "${BLUE}Cancelled${NC}" ;;
            *) printf "${BLUE}No recent runs${NC}" ;;
        esac
        echo ""

        echo ""
        printf "${BLUE}%s${NC}\n" "$(printf '=%.0s' {1..75})"
    }

    log_info "Starting DevOps monitor (Ctrl+C to exit)..."
    sleep 1

    # Trap Ctrl+C to clean up
    trap 'clear; echo -e "${GREEN}✓ Monitor stopped${NC}"; exit 0' INT TERM

    while true; do
        draw_monitor
        sleep 60
    done
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
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/v1/health"]
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

Usage: ./dev.sh [command] [options]

Commands:
  setup             Initial setup (build images, install dependencies)
  start             Start all development containers
  stop              Stop all containers
  restart           Restart all containers
  status            Show container status and health checks
  clean [--gitignore]
                    Remove all containers, images, and volumes
                    --gitignore, -g: Remove only gitignored files
  test [--watch]    Run all tests (backend + frontend)
                    --watch, -w: Run tests in watch mode
  docs              Generate all reports and serve documentation site
  logs              Show logs from all containers
  shell-api         Open shell in API container
  shell-frontend    Open shell in frontend container
  rebuild           Rebuild all containers from scratch
  monitor           Real-time DevSecOps dashboard with RAG status indicators
                    • Local: containers, tests, coverage, security, dependencies
                    • GitHub: CI/CD workflow status (public API, no auth required)
                    • Updates every 60 seconds
  help              Show this help message

Examples:
  ./dev.sh setup              # First-time setup
  ./dev.sh start              # Start development
  ./dev.sh status             # Check container status
  ./dev.sh monitor            # Launch comprehensive DevSecOps dashboard
  ./dev.sh logs               # Watch logs
  ./dev.sh test               # Run tests once
  ./dev.sh test --watch       # Run tests in watch mode
  ./dev.sh clean              # Remove containers and optionally gitignored files
  ./dev.sh clean --gitignore  # Remove only gitignored files
  ./dev.sh docs               # Generate reports & serve docs

Monitor Dashboard Features:
  ✅ Green   - Healthy/Passing (80%+ coverage, 0 critical issues, all tests pass)
  ⚠️  Amber   - Warning (60-79% coverage, minor issues, partial services)
  ❌ Red     - Critical (< 60% coverage, failed tests, critical vulnerabilities)
  ○  Grey    - Unknown/Not Available

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
    status)
        show_status
        ;;
    clean)
        shift  # Remove 'clean' from arguments
        clean_dev "$@"
        ;;
    test)
        shift  # Remove 'test' from arguments
        run_tests "$@"
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
    monitor)
        monitor_workflows
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
