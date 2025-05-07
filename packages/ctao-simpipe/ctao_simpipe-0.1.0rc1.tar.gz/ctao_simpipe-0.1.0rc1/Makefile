###
export CHART_NAME=simpipe
export CHART_LOCATION=chart
export DEV_IMAGE_SUFFIX=-prod
include dpps-aiv-toolkit/Makefile

# optionally include .env for SOFTWARE_DOWNLOAD_SECRET to make local development easier
-include .env

DOWNLOAD_URL=https://syncandshare.desy.de/index.php/s
SOFTWARE_DOWNLOAD_SECRET?=

software/%: | software
	@if [ -z "${SOFTWARE_DOWNLOAD_SECRET}" ]; then echo "Please set the SOFTWARE_DOWNLOAD_SECRET env variable"; exit 1; fi
	curl -fL -o $@  "${DOWNLOAD_URL}/${SOFTWARE_DOWNLOAD_SECRET}/download?path=/&files=$*"

software:
	mkdir -p software

build-dev-docker: software/corsika7.7_simtelarray_20240913.tar.gz
build-dev-docker: software/corsikaOptPatch-77500_2024-02-05.tar.gz
