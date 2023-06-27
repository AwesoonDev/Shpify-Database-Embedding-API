#!/bin/bash

# Get the number of workers from the first script argument
NUM_WORKERS=$1

# Verify that num_workers is a number
if ! [[ "$NUM_WORKERS" =~ ^[0-9]+$ ]]
then
    echo "Error: Argument must be a positive integer."
    exit 1
fi

# Start the specified number of workers
for ((i=1; i<=NUM_WORKERS; i++))
do
    echo "Starting worker $i..."
    celery -A awesoon.celery.tasks worker --loglevel=info &
done

# Wait for all background processes to finish
wait
