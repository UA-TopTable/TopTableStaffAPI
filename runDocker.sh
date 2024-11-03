#!/bin/bash

docker build -t staffapi .
docker run -dp 8000:8000 -v ./app:/app staffapi