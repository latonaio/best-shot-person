#!/bin/bash

docker build --build-arg DEVICE_NAME=shiva --build-arg NEXT_DEVICE_NAME=shiva --build-arg NEXT_USER=XXXXX -t best-shot-person:latest ./
