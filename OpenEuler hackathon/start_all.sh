#!/bin/bash

# Start backend in background
echo "Starting backend..."
cd backend && python3 metrics.py &
BACKEND_PID=$!

# Start frontend in background  
echo "Starting frontend..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Both services started. Press Ctrl+C to stop all."

# Wait for both processes
wait