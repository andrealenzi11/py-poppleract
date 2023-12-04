#!/bin/bash

VERSION=0.0.5

docker login

echo -e "\n >>> Building base image ..."
docker build -t andrealenzi/poppleract-base:23.12_5.3.3 -f base.Dockerfile .
docker push andrealenzi/poppleract-base:23.12_5.3.3

echo -e "\n >>> Building services image ..."
docker build -t andrealenzi/poppleract-services:${VERSION} -f services.Dockerfile .
docker push andrealenzi/poppleract-services:${VERSION}
