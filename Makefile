# Makefile

PROJECT_NAME = iot-data-platform-simulator
COMPOSE = docker compose

.PHONY: up down build logs restart clean

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

logs:
	$(COMPOSE) logs -f

restart:
	$(MAKE) down
	$(MAKE) up

clean:
	$(COMPOSE) down -v --remove-orphans
