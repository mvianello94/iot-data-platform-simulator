# Makefile

PROJECT_NAME = iot-data-platform
COMPOSE = docker compose

.PHONY: up down build rebuild logs restart clean

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	COMPOSE_BAKE=true $(COMPOSE) build

rebuild:
	$(MAKE) build
	$(MAKE) up

logs:
	@if [ -z "$(SERVICE)" ]; then \
		$(COMPOSE) logs -f; \
	else \
		$(COMPOSE) logs -f $(SERVICE); \
	fi

restart:
	$(MAKE) down
	$(MAKE) up

clean:
	$(COMPOSE) down -v --remove-orphans
