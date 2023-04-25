#!/bin/bash

docker-compose --project-name manuscript-local \
               --file project/docker-compose.yml \
               down -v