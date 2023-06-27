# Project configuration
PROJECT_NAME = shop-api

# General Parameters
TOPDIR = $(shell git rev-parse --show-toplevel)
CONDA_SH := $(shell find ~/*conda*/etc -name conda.sh | tail -1)
ACTIVATE := source $(CONDA_SH) && conda activate $(PROJECT_NAME)

default: help

help: # Display help
	@awk -F ':|##' \
		'/^[^\t].+?:.*?##/ {\
			printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
		}' $(MAKEFILE_LIST) | sort

run: ## Start the service locally
	cd $(TOPDIR) && \
	FLASK_APP=awesoon.app.py \
	flask run --host=0.0.0.0 --no-debugger --no-reload -p $(PORT)

build-docker: ## Build the docker image
	@docker-compose -f deploy/docker_compose/docker-compose.dev.yml build

run-docker: ## Run the docker image
	@docker-compose -f deploy/docker_compose/docker-compose.dev.yml up

stop-docker: # Stop and remove containers and networks
	@docker-compose -f deploy/docker_compose/docker-compose.dev.yml down

run-celery: # Run celery workers
	./entrypoint_celery.sh $(NUM_WORKERS)

test: ## Run tox
	tox

clean-code: ## Remove unwanted files in this project (!DESTRUCTIVE!)
	@cd $(TOPDIR) && git clean -ffdx && git reset --hard

clean-docker: ## Remove all docker artifacts for this project (!DESTRUCTIVE!)
	@docker image rm -f $(shell docker image ls --filter reference='$(DOCKER_REPO)' -q) || true

setup: ## Setup the full environment (default)
	conda env update -f environment.yml

.PHONY: default help start build-docker run-docker stop-docker test clean-code clean-docker code setup
