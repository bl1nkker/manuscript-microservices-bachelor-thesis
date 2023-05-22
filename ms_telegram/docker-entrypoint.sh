#!/bin/bash
./wait-for-it.sh rabbitmq:5672 -- python -m telegram.py
