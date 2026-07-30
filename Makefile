# =============================================================================
# SupplySight AI — Makefile
# Purpose: Standard developer entry points for setup, lint, test, and Docker.
# Targets are scaffolding placeholders until application code exists.
# =============================================================================

.PHONY: help setup up down logs lint test clean

# Default target — print available commands
help:
	@echo "SupplySight AI — common targets"
	@echo "  make setup   - Initial local environment setup (placeholder)"
	@echo "  make up      - Start Docker Compose services"
	@echo "  make down    - Stop Docker Compose services"
	@echo "  make logs    - Tail Compose logs"
	@echo "  make lint    - Run linters (placeholder)"
	@echo "  make test    - Run test suites (placeholder)"
	@echo "  make clean   - Remove ephemeral build/cache artifacts"

# Bootstrap local tooling and env files (expand in scripts/setup/)
setup:
	@echo "[SupplySight] Setup placeholder — see scripts/setup/ and CONTRIBUTING.md"
	@test -f .env || cp .env.example .env
	@echo "[SupplySight] .env ready (edit credentials before use)"

# Start infrastructure / services defined in docker-compose.yml
up:
	docker compose up -d

# Stop services and remove containers (volumes retained)
down:
	docker compose down

# Follow logs from all Compose services
logs:
	docker compose logs -f

# Lint frontend and backend (wire tools in later phases)
lint:
	@echo "[SupplySight] Lint placeholder — configure ESLint/Ruff when code lands"

# Run unit and integration tests (wire runners in later phases)
test:
	@echo "[SupplySight] Test placeholder — see tests/ and package-local test dirs"

# Clean common cache directories (safe defaults)
clean:
	@echo "[SupplySight] Cleaning caches..."
	-rm -rf frontend/.next frontend/node_modules/.cache
	-rm -rf backend/.pytest_cache .pytest_cache
	-find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	@echo "[SupplySight] Clean complete"
