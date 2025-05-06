VERSION := $(shell python -c 'import setuptools_scm; print(setuptools_scm.get_version())')

IMAGE_VERSION := $(shell git describe --tags --abbrev=0 | sed 's/^v//')
BIN_NAME = neutrino
IMAGE_NAME = $(BIN_NAME):$(IMAGE_VERSION)
DOCKER_ID_USER = timeplus
FULLNAME=$(DOCKER_ID_USER)/${IMAGE_NAME}

.PHONY: docker

version:
	echo "Version: $(VERSION)"

build:
	python3 -m pip install --upgrade build
	python3 -m build

install: build
	python3 -m pip install --upgrade dist/timeplus_neutrino-$(VERSION).tar.gz

lint:
	flake8 ./src --count --select=E9,F63,F7,F82 --ignore=E501,W293 --show-source --statistics
	flake8 ./src --count --exit-zero --max-complexity=10 --ignore=E501,W503,W293 --max-line-length=127 --statistics

format:
	black ./src

upload:
	twine upload  --config-file ./.pypirc  dist/*

mcp_client:
	.venv/bin/python -m neutrino.mcp.cli_client .venv/lib/python3.13/site-packages/neutrino/mcp/main.py

mcp_client_ui:
	.venv/bin/python -m neutrino.mcp.ui_client .venv/lib/python3.13/site-packages/neutrino/mcp/main.py

mcp_api_server:
	.venv/bin/python -m neutrino.mcp.application_server .venv/lib/python3.13/site-packages/neutrino/mcp/main.py

docker: Dockerfile
	docker buildx build \
		--no-cache -t $(FULLNAME) \
		--build-arg VERSION=$(VERSION) \
		--platform linux/arm64,linux/amd64 \
		--builder container \
		--push .

