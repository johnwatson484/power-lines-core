#!/usr/bin/env sh

# Clone repositories managed by this project into parent repo
set -e
projectRoot=$(a="/$0"; a=${a%/*}; a=${a:-.}; a=${a#/}/; cd "$a/.." || return; pwd)

(
  cd "${projectRoot}"
  cd ..

  printf "\nCloning repositories\n"

  test -d power-lines-data-service \
    && >&2 echo "The 'power-lines-data-service' directory already exists. Skipping." \
    || git clone https://github.com/johnwatson484/power-lines-data-service.git
  test -d power-lines-fixture-service \
    && >&2 echo "The 'power-lines-data-fixture-service' directory already exists. Skipping." \
    || git clone https://github.com/johnwatson484/power-lines-fixture-service.git
  test -d power-lines-analysis-service \
    && >&2 echo "The 'power-lines-data-analysis-service' directory already exists. Skipping." \
    || git clone https://github.com/johnwatson484/power-lines-analysis-service.git

  printf "\nBuilding images\n"

  scripts/build
)

