docker-compose \
  -f ../power-lines-data-service/docker-compose.yaml \
  -f ../power-lines-data-service/docker-compose.override.yaml \
  -f ../power-lines-data-service/docker-compose.link.yaml \
  down \
  -v

docker-compose \
  -f ../power-lines-fixture-service/docker-compose.yaml \
  -f ../power-lines-fixture-service/docker-compose.override.yaml \
  -f ../power-lines-data-service/docker-compose.link.yaml \
  down \
  -v

docker network rm power-lines