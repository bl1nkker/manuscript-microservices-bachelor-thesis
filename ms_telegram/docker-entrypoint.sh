#!/bin/bash
./wait-for-it.sh rabbitmq:5672 -- python3 -m telegram.py
