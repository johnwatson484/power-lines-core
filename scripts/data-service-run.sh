#!/bin/sh

docker exec -it -d power-lines-data-service /bin/sh -c "dotnet run --project ./PowerLinesDataService $@"
