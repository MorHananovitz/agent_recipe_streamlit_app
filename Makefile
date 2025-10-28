.PHONY: help setup install run clean env

# Variables
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip
APP_FILE := recipe_app/app.py
PORT := 8501

# Colors for terminal output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Recipe App Makefile Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: clean env install ## Complete setup: create environment and install dependencies
	@echo "$(GREEN)✓ Setup complete! Run 'make run' to start the app$(NC)"

env: ## Create virtual environment
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(NC)"

install: ## Install all dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install -r recipe_app/requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

run: ## Run the Streamlit app and open in Chrome
	@echo "$(YELLOW)Starting Recipe App...$(NC)"
	@echo "$(GREEN)Opening Chrome browser at http://localhost:$(PORT)$(NC)"
	@sleep 2 && open -a "Google Chrome" http://localhost:$(PORT) &
	@$(VENV_PYTHON) -m streamlit run $(APP_FILE) --server.port=$(PORT)

dev: ## Run the app without opening browser
	@echo "$(YELLOW)Starting Recipe App in dev mode...$(NC)"
	@echo "$(GREEN)App will be available at http://localhost:$(PORT)$(NC)"
	@$(VENV_PYTHON) -m streamlit run $(APP_FILE) --server.port=$(PORT)

test-env: ## Test if environment is properly set up
	@if [ -d "$(VENV)" ]; then \
		echo "$(GREEN)✓ Virtual environment exists$(NC)"; \
	else \
		echo "$(RED)✗ Virtual environment not found. Run 'make setup'$(NC)"; \
		exit 1; \
	fi
	@if $(VENV_PYTHON) -c "import streamlit" 2>/dev/null; then \
		echo "$(GREEN)✓ Dependencies are installed$(NC)"; \
	else \
		echo "$(RED)✗ Dependencies not installed. Run 'make install'$(NC)"; \
		exit 1; \
	fi

clean: ## Remove virtual environment and cache files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@rm -rf $(VENV)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

reinstall: clean setup ## Clean and reinstall everything
	@echo "$(GREEN)✓ Reinstallation complete$(NC)"

update: ## Update all dependencies
	@echo "$(YELLOW)Updating dependencies...$(NC)"
	@$(VENV_PIP) install --upgrade -r recipe_app/requirements.txt
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

freeze: ## Generate requirements.txt from current environment
	@echo "$(YELLOW)Freezing current dependencies...$(NC)"
	@$(VENV_PIP) freeze > recipe_app/requirements.txt
	@echo "$(GREEN)✓ requirements.txt updated$(NC)"

info: ## Show project information
	@echo "$(GREEN)Project Information:$(NC)"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Virtual Env: $(VENV)"
	@echo "  App File: $(APP_FILE)"
	@echo "  Port: $(PORT)"
	@if [ -d "$(VENV)" ]; then \
		echo "  Streamlit: $(shell $(VENV_PYTHON) -m streamlit version 2>/dev/null | head -n 1 || echo 'Not installed')"; \
	fi

