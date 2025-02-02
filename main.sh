#!/bin/bash

# Run the main script
python3 src/main.py

# Start the server
cd public && python3 -m http.server 8888