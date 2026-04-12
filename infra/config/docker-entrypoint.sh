#!/bin/sh
set -e

# Configurable gunicorn settings (override via environment variables)
GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
GUNICORN_BIND="${GUNICORN_BIND:-127.0.0.1:5000}"

# Next.js standalone server settings
NEXTJS_PORT="${NEXTJS_PORT:-3000}"
NEXTJS_HOSTNAME="${NEXTJS_HOSTNAME:-127.0.0.1}"

# Graceful shutdown helper (shared by signal trap and the process-monitor loop)
cleanup() {
    echo "Shutting down services..."
    nginx -s quit 2>/dev/null || true
    if [ -n "$NEXTJS_PID" ]; then
        kill -TERM "$NEXTJS_PID" 2>/dev/null || true
        wait "$NEXTJS_PID" 2>/dev/null || true
    fi
    if [ -n "$GUNICORN_PID" ]; then
        kill -TERM "$GUNICORN_PID" 2>/dev/null || true
        wait "$GUNICORN_PID" 2>/dev/null || true
    fi
}

shutdown() {
    cleanup
    exit 0
}
trap shutdown TERM INT

# Substitute the configured Next.js address into the nginx reverse-proxy config
# so that overriding NEXTJS_PORT/NEXTJS_HOSTNAME is reflected end-to-end.
# Validate values first to prevent unexpected sed behaviour.
case "$NEXTJS_PORT" in
    *[!0-9]*) echo "Invalid NEXTJS_PORT: $NEXTJS_PORT"; exit 1 ;;
esac
case "$NEXTJS_HOSTNAME" in
    *[!a-zA-Z0-9.\-]*) echo "Invalid NEXTJS_HOSTNAME: $NEXTJS_HOSTNAME"; exit 1 ;;
esac
sed -i "s|127\.0\.0\.1:3000|${NEXTJS_HOSTNAME}:${NEXTJS_PORT}|" /etc/nginx/sites-available/default

# Start nginx as daemon
nginx

echo "nginx started"

# Start Next.js standalone server in the background
PORT="$NEXTJS_PORT" HOSTNAME="$NEXTJS_HOSTNAME" node /app/frontend/server.js &
NEXTJS_PID=$!

echo "Next.js started (PID: $NEXTJS_PID)"

# Start gunicorn with the ASGI worker in the background
gunicorn -k uvicorn.workers.UvicornWorker --bind "$GUNICORN_BIND" --workers "$GUNICORN_WORKERS" --timeout "$GUNICORN_TIMEOUT" backend.api.main:app &
GUNICORN_PID=$!

echo "gunicorn started (PID: $GUNICORN_PID)"

# Monitor both processes; if either exits unexpectedly, shut everything down
# and exit with a non-zero code so the container orchestrator can restart.
while true; do
    if ! kill -0 "$NEXTJS_PID" 2>/dev/null; then
        echo "Next.js process (PID $NEXTJS_PID) exited unexpectedly"
        break
    fi
    if ! kill -0 "$GUNICORN_PID" 2>/dev/null; then
        echo "Gunicorn process (PID $GUNICORN_PID) exited unexpectedly"
        break
    fi
    sleep 5
done

cleanup
exit 1
