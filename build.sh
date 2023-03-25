#!/usr/bin/env bash

docker build -t alpaca-image .

docker run alpaca-image python3 /app/main.py