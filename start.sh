#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "🚀 Starting OutboundAI..."

if [ -f ".env" ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

echo "🌐 Starting FastAPI server on port 8000..."
uvicorn server:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

sleep 2

echo "🤖 Starting LiveKit agent worker..."
python agent.py start

kill $SERVER_PID 2>/dev/null || true
