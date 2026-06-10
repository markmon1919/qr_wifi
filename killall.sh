#!/bin/bash

declare -a PIDS=(``)

PIDS+=(`ps aux | grep "'[p]ython'\|uvicorn" | grep -v grep | awk '{print $2}'`)
port_pid=(`lsof -i :8000 | awk '{print$2}' | tail -n +2`)
port_pid2=(`lsof -i :7777 | awk '{print$2}' | tail -n +2`)

if [[ -z "$port_pid" ]]; then
    PIDS+=("$port_pid" "$port_pid2")
fi

# Check if list is empty
if [[ ${#PIDS[@]} -eq 0 ]]; then
    echo "No processes found."
    exit 0
fi

# Kill the processes
for pid in "${PIDS[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid"
        echo "Killing Process: $pid"
    else
        echo "PID $pid does not exist or already terminated."
    fi
done
