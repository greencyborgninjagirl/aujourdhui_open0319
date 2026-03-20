#!/bin/bash
cd "$(dirname "$0")"
echo "Starting API at http://127.0.0.1:8000 (local dev only) ..."
uvicorn backend_api:app --reload --host 127.0.0.1 --port 8000
