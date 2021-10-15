#!/bin/bash

docker build --build-arg DEVICE_NAME=shiva --build-arg NEXT_DEVICE_NAME=shiva --build-arg NEXT_USER=aisin -t best-shot-person:latest ./
