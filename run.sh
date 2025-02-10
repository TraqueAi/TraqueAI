#!/bin/bash

# Pull the model (only needs to be done once)
docker exec -it ollamaa ollama pull llama3:8b

# Run the command or script you need
docker exec -it ollamaa ollama run nomic-embed-text

# Attach to the bayesrag container
docker attach bayesrag_cont
