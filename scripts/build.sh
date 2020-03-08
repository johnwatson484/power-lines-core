#!/usr/bin/env sh
docker-compose \
  -f ../power-lines-data-service/docker-compose.yaml \
  -f ../power-lines-data-service/docker-compose.override.yaml \
  build $@

docker-compose \
  -f ../power-lines-fixture-service/docker-compose.yaml \
  -f ../power-lines-fixture-service/docker-compose.override.yaml \
  build $@

docker-compose \
  -f ../power-lines-analysis-service/docker-compose.yaml \
  -f ../power-lines-analysis-service/docker-compose.override.yaml \
  build $@
