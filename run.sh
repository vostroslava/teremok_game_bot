#!/bin/bash

# Activate virtual env if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load variables
export $(grep -v '^#' .env | xargs) 2>/dev/null

# Run
python3 main.py
