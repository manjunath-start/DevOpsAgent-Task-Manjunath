#!/bin/bash
# Run a CPU-intensive container for testing
docker run -d --name stress_test \
  polinux/stress \
  stress --cpu 2 --timeout 600s
