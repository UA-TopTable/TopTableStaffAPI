#!/bin/bash

docker build -t staffapi .
docker run -dp 5000:5000 -v ./app:/app staffapi