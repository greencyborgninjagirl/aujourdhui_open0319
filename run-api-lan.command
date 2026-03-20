#!/bin/bash
# 局域网内测：手机与电脑同一 WiFi 时，手机可访问此 API
# 启动后在本机浏览器打开 http://本机IP:8000/docs 验证
cd "$(dirname "$0")"
echo "Starting API for LAN test at http://0.0.0.0:8000"
echo "Use your computer's LAN IP (e.g. 192.168.x.x) in frontend config."
uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000
