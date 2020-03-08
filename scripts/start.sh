#!/usr/bin/env sh
if [ -z "$(docker network ls --filter name=^power-lines$ --format={{.Name}})" ]; then
  echo "Creating power-lines Docker network"
  docker network create power-lines
fi

docker-compose \
  -f ../power-lines-data-service/docker-compose.yaml \
  -f ../power-lines-data-service/docker-compose.override.yaml \
  -f ../power-lines-data-service/docker-compose.link.yaml \
  up \
  --detach

docker-compose \
  -f ../power-lines-fixture-service/docker-compose.yaml \
  -f ../power-lines-fixture-service/docker-compose.override.yaml \
  -f ../power-lines-data-service/docker-compose.link.yaml \
  up \
  --detach \
  --scale power-lines-message=0

docker-compose \
  -f ../power-lines-analysis-service/docker-compose.yaml \
  -f ../power-lines-analysis-service/docker-compose.override.yaml \
  -f ../power-lines-analysis-service/docker-compose.link.yaml \
  up \
  --detach \
  --scale power-lines-message=0
