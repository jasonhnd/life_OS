# Life OS · Common dev commands
# Tab-indented (POSIX make requires tabs, not spaces).

.PHONY: help test test-fast test-verbose lint lint-fix bash-check stats install update docs-check ci

help: ## Show this help message
	@echo "Life OS · dev commands"
	@echo ""
	@echo "Common tasks:"
	@echo "  make test          Run pytest suite"
	@echo "  make test-fast     Run pytest, fail fast on first error"
	@echo "  make test-verbose  Run pytest with verbose output"
	@echo "  make lint          Run ruff lint check"
	@echo "  make lint-fix      Run ruff lint check + auto-fix"
	@echo "  make bash-check    Bash syntax check on scripts"
	@echo "  make stats         Show compliance stats from violations.md"
	@echo "  make install       Install Python deps via uv"
	@echo "  make update        Update Python deps via uv"
	@echo "  make ci            Full CI suite: install + lint + test + bash-check"
	@echo ""
	@echo "Tools:"
	@echo "  python3 tools/cli.py list              Show all life-os-tool commands"
	@echo "  python3 tools/cli.py stats             Compliance stats"
	@echo "  python3 tools/cli.py rebuild-session-index  Recompile sessions INDEX"
	@echo "  python3 tools/cli.py rebuild-concept-index  Recompile concepts INDEX"
	@echo "  python3 tools/cli.py extract           Concept candidates from stdin"
	@echo "  python3 tools/cli.py seed-concepts     Bootstrap concept graph"
	@echo "  python3 tools/cli.py backup --dry-run  Snapshot/violations rotation preview"

test: ## Run pytest suite
	python3 -m pytest tests/

test-fast: ## Run pytest, stop on first failure
	python3 -m pytest tests/ -x

test-verbose: ## Run pytest with -v
	python3 -m pytest tests/ -v

lint: ## Run ruff lint check
	python3 -m ruff check tools/ tests/

lint-fix: ## Run ruff lint check + auto-fix safe issues
	python3 -m ruff check tools/ tests/ --fix

bash-check: ## Bash syntax check on all .sh scripts
	@for s in scripts/*.sh evals/run-eval.sh; do \
		echo "Checking $$s..."; \
		bash -n "$$s" || exit 1; \
	done
	@echo "✅ All bash scripts syntax OK"

stats: ## Show compliance violation stats
	python3 tools/cli.py stats

install: ## Install Python deps via uv (requires uv)
	uv sync --extra dev

update: ## Update Python deps via uv
	uv lock --upgrade

ci: install lint test bash-check ## Full CI suite (mirrors .github/workflows/test.yml)
	@echo "✅ CI suite passed"
