#!/bin/bash

VERSION=$(python3 -c "import sys, json; print(json.load(sys.stdin)['version'])" < 'version.json')
BASE_IMAGE_NAME=andrealenzi/poppleract-base:23.12_5.3.3
SERVICES_IMAGE_NAME=andrealenzi/poppleract-services:${VERSION}
echo "(*) VERSION:" "${VERSION}"
echo "(*) BASE_IMAGE_NAME:" "${BASE_IMAGE_NAME}"
echo "(*) SERVICES_IMAGE_NAME:" "${SERVICES_IMAGE_NAME}"

echo -e "\n >>> Building base image ..."
if docker image inspect "${BASE_IMAGE_NAME}" >/dev/null 2>&1; then
    echo "- Base image already exists locally!"
else
    docker build -t "${BASE_IMAGE_NAME}" -f base.Dockerfile .
fi

echo -e "\n >>> Building services image ..."
if docker image inspect "${SERVICES_IMAGE_NAME}" >/dev/null 2>&1; then
    echo "- Services image already exists locally!"
else
    docker build -t "${SERVICES_IMAGE_NAME}" -f services.Dockerfile .
fi

# docker login
# docker push "${BASE_IMAGE_NAME}"
# docker push "${SERVICES_IMAGE_NAME}"

exit 0
