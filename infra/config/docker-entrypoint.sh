#!/bin/sh
set -e

# Configurable gunicorn settings (override via environment variables)
GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
GUNICORN_BIND="${GUNICORN_BIND:-127.0.0.1:5000}"

# Trap SIGTERM and SIGINT for graceful shutdown
shutdown() {
    echo "Shutting down services..."
    nginx -s quit 2>/dev/null || true
    if [ -n "$GUNICORN_PID" ]; then
        kill -TERM "$GUNICORN_PID" 2>/dev/null || true
        wait "$GUNICORN_PID" 2>/dev/null || true
    fi
    exit 0
}
trap shutdown TERM INT

# Start nginx as daemon
nginx

echo "nginx started"

# Start gunicorn with the ASGI worker in the background
gunicorn -k uvicorn.workers.UvicornWorker --bind "$GUNICORN_BIND" --workers "$GUNICORN_WORKERS" --timeout "$GUNICORN_TIMEOUT" api:app &
GUNICORN_PID=$!

echo "gunicorn started (PID: $GUNICORN_PID)"

# Wait for gunicorn; propagate its exit code so orchestrators detect failures
wait "$GUNICORN_PID"
EXIT_CODE=$?
exit $EXIT_CODE
