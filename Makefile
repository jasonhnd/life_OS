# Life OS · Common dev commands
# Tab-indented (POSIX make requires tabs, not spaces).

.PHONY: help test test-fast test-verbose test-integration lint lint-fix bash-check stats install update docs-check ci ci-integration eval-tools

help: ## Show this help message
	@echo "Life OS · dev commands"
	@echo ""
	@echo "Common tasks:"
	@echo "  make test             Run pytest suite (integration tests skipped by default)"
	@echo "  make test-fast        Run pytest, fail fast on first error"
	@echo "  make test-verbose     Run pytest with verbose output"
	@echo "  make test-integration Run only @pytest.mark.integration tests (network / external services)"
	@echo "  make lint             Run ruff lint check"
	@echo "  make lint-fix         Run ruff lint check + auto-fix"
	@echo "  make bash-check       Bash syntax check on scripts"
	@echo "  make stats            Show compliance stats from violations.md"
	@echo "  make install          Install Python deps via uv"
	@echo "  make update           Update Python deps via uv"
	@echo "  make ci               Full CI suite: install + lint + test + bash-check"
	@echo "  make ci-integration   Integration CI: install + lint + test-integration + bash-check"
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

test-integration: ## Run only @pytest.mark.integration tests (opt-in; requires LIFEOS_INTEGRATION=1 for real external calls)
	python3 -m pytest tests/ -m integration

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

ci-integration: install lint test-integration bash-check ## Integration CI (mirrors .github/workflows/integration.yml)
	@echo "✅ Integration CI suite passed"

eval-tools: ## Run R4.5 machine-verifiable tool scenario runner (not in default `ci`)
	bash evals/run-tool-eval.sh
