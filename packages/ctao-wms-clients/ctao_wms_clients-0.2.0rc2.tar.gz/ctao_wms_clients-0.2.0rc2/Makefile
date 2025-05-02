###
export CHART_NAME=wms
export CHART_LOCATION=chart
export DOCKER_IMAGE_CONTEXT=docker/client

DEV_VERSION=0.2.0-dev

include dpps-aiv-toolkit/Makefile


# TODO: move this to kit
export TEST_ARTIFACTS_PATH ?= $(PWD)
export TEST_REPORT_CONFIG ?= $(PWD)/aiv-config.yml
export TEX_CONTENT_PATH ?= $(PWD)/report



build-dev-server-images:
	docker build docker/client/ -t harbor.cta-observatory.org/dpps/wms-client:${DEV_VERSION}
	docker build docker/server/ -t harbor.cta-observatory.org/dpps/wms-server:${DEV_VERSION}
	docker build docker/ce/ -t harbor.cta-observatory.org/dpps/wms-ce:${DEV_VERSION}
	./kind -n kind-dpps-test-local load docker-image \
		harbor.cta-observatory.org/dpps/wms-client:${DEV_VERSION} \
		harbor.cta-observatory.org/dpps/wms-ce:${DEV_VERSION} \
		harbor.cta-observatory.org/dpps/wms-server:${DEV_VERSION}

dev: build-dev-server-images

.PHONY: build-dev-server-images
