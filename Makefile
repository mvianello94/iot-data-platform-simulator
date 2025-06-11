# Makefile

PROJECT_NAME = iot-data-platform
COMPOSE = docker compose

.PHONY: up down build rebuild logs restart clean

## Service Management

# Brings up Docker Compose services.
# Use 'make up SERVICE=your_service_name' to bring up a single service.
up:
	@if [ -z "$(SERVICE)" ]; then \
		$(COMPOSE) up -d; \
	else \
		$(COMPOSE) up -d $(SERVICE); \
	fi

# Brings down Docker Compose services.
# Use 'make down SERVICE=your_service_name' to bring down a single service.
down:
	@if [ -z "$(SERVICE)" ]; then \
		$(COMPOSE) down; \
	else \
		$(COMPOSE) down $(SERVICE); \
	fi

# Builds Docker Compose services.
# Use 'make build SERVICE=your_service_name' to build a single service.
build:
	@if [ -z "$(SERVICE)" ]; then \
		COMPOSE_BAKE=true $(COMPOSE) build; \
	else \
		COMPOSE_BAKE=true $(COMPOSE) build $(SERVICE); \
	fi

# Rebuilds and brings up Docker Compose services.
# Use 'make rebuild SERVICE=your_service_name' to rebuild a single service.
rebuild:
	@if [ -z "$(SERVICE)" ]; then \
		$(MAKE) build; \
		$(MAKE) up; \
	else \
		$(MAKE) build SERVICE=$(SERVICE); \
		$(MAKE) up SERVICE=$(SERVICE); \
	fi

# Displays logs for Docker Compose services.
# Use 'make logs SERVICE=your_service_name' to view logs for a single service.
logs:
	@if [ -z "$(SERVICE)" ]; then \
		$(COMPOSE) logs -f; \
	else \
		$(COMPOSE) logs -f $(SERVICE); \
	fi

# Restarts all Docker Compose services.
restart:
	$(MAKE) down
	$(MAKE) up

## Cleaning

# Removes containers, networks, volumes, and dangling images.
clean:
	$(COMPOSE) down -v --remove-orphans
