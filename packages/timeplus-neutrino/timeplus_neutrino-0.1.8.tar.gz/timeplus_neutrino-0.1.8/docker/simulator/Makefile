IMAGE_VERSION := $(shell git rev-parse --short HEAD)
BIN_NAME = cdcsimulator
IMAGE_NAME = $(BIN_NAME):$(IMAGE_VERSION)
DOCKER_ID_USER = timeplus
FULLNAME=$(DOCKER_ID_USER)/${IMAGE_NAME}

.PHONY: docker

docker: Dockerfile
	docker buildx build \
		--no-cache -t $(FULLNAME) \
		--build-arg VERSION=$(VERSION) \
		--platform linux/arm64,linux/amd64 \
		--builder container \
		--push .