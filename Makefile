PROJECT_NAME = chatbot
TEST_FOLDER = tests
APPLICATION = chatbot.api.main:app

.PHONY:default
default: help

.PHONY: help
help:
	@echo "All Commands:"
	@echo "	Code Style:"
	@echo "		check - Check format style."
	@echo "		format - Format code style."
	@echo "		typecheck - Check types in code"
	@echo "	Env:"
	@echo "		clean - Remove temp files."
	@echo "		down - Stop containers."
	@echo "		db_upgrade - Apply database migrations."
	@echo "		db_generate_revision - Generate database migrations."
	@echo "   	run - Run application in development mode."
	@echo "		unit-test - Run unit tests."
	@echo "		integration-test - Run integration tests."
	@echo " 	coverage - Run tests and gather coverage data."
	@echo "		up - Start containers."

.PHONY: format
format:
	@echo ""
	@echo "FORMATTING CODE:"
	@echo ""
	ruff format $(PROJECT_NAME) $(TEST_FOLDER)
	ruff check --select I --fix $(PROJECT_NAME) $(TEST_FOLDER)

	@echo ""
	@echo "CHECKING CODE STILL NEEDS FORMATTING:"
	@echo ""
	ruff format --check $(PROJECT_NAME) $(TEST_FOLDER)

	@echo ""
	@echo "CHECKING TYPING"
	@echo ""
	@make typecheck

	@echo ""
	@echo "CHECKING CODE STYLE"
	@echo ""
	ruff check $(PROJECT_NAME) $(TEST_FOLDER)

	@echo ""
	@echo "SORT IMPORTS"
	@echo ""
	ruff check --select I $(PROJECT_NAME) $(TEST_FOLDER)

	@echo ""
	@echo "CHECKING SECURITY ISSUES"
	@echo ""
	bandit -r $(PROJECT_NAME)

.PHONY: clean
clean:
	- @find . -name "*.pyc" -exec rm -rf {} \;
	- @find . -name "__pycache__" -delete
	- @find . -name "*.pytest_cache" -exec rm -rf {} \;
	- @find . -name "*.mypy_cache" -exec rm -rf {} \;

.PHONY: typecheck
typecheck:
	mypy $(PROJECT_NAME)/

.PHONY: run
run:
	docker compose -f infrastructure/docker/docker-compose.yaml up -d
	uvicorn $(APPLICATION) --reload

.PHONY: db_upgrade
db_upgrade:
	alembic upgrade head

.PHONY: db_generate_revision
db_generate_revision:
	alembic revision --autogenerate

.PHONY: up
up:
	docker compose -f infrastructure/docker/docker-compose.yaml up -d

.PHONY: down
down:
	docker compose -f infrastructure/docker/docker-compose.yaml down --remove-orphans

.PHONY: db_upgrade_test
db_upgrade_test:
	DB_USER=postgres DB_PASS=chatbot_test DB_HOST=127.0.0.1 DB_PORT=5435 DB_NAME=chatbot_test DB_POOL_SIZE=5 DB_MAX_OVERFLOW=0 alembic upgrade head

.PHONY: unit-test
unit-test:
	@if [ -n "$(file)" ]; then \
		pytest $(file) -vv; \
	else \
		pytest tests/unit/ tests/acceptance/ -vv; \
	fi

.PHONY: integration-test
integration-test:
	- docker container stop chatbot_test_db
	- docker container rm chatbot_test_db
	docker run -d --name chatbot_test_db -e "POSTGRES_DB=chatbot_test" -e "POSTGRES_PASSWORD=chatbot_test" -P -p 127.0.0.1:5435:5432 postgres:14-alpine
	sleep 2
	@make db_upgrade_test
	@if [ -n "$(file)" ]; then \
		pytest $(file) -vv; \
	else \
		pytest tests/integration/ -vv; \
	fi
	docker container stop chatbot_test_db
	docker container rm chatbot_test_db

.PHONY: coverage
coverage:
	coverage run -m pytest tests/unit/ -vv
	coverage report -m

.PHONY: db_test_drop
db_test_drop:
	docker container ls -a | grep chatbot_test_db | awk '{print $$1}' | xargs docker container stop | xargs docker container rm

.PHONY: db_drop
db_drop:
	docker container ls -a | grep chatbot_db | awk '{print $$1}' | xargs docker container stop | xargs docker container rm
