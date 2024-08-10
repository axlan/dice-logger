#!/usr/bin/env bash

docker build -t mqtt-dice-logger .
docker rm -f dice-logger
docker run -itd --restart=always -p 2020:2020 -v $(pwd)/datadir:/datadir --name dice-logger mqtt-dice-logger
