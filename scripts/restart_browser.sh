#!/bin/bash
# 重启浏览器服务，清理僵尸进程
echo "[$(date)] 重启浏览器服务..."

# 停止旧进程
pkill -f "google-chrome.*18800" 2>/dev/null || true
sleep 2

# 启动新进程
nohup google-chrome-stable \
  --remote-debugging-port=18800 \
  --user-data-dir=/root/.openclaw/browser/openclaw/user-data \
  --no-first-run \
  --no-default-browser-check \
  --disable-sync \
  --disable-background-networking \
  --disable-component-update \
  --disable-features=Translate,MediaRouter \
  --disable-session-crashed-bubble \
  --hide-crash-restore-bubble \
  --password-store=basic \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --disable-setuid-sandbox \
  --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  --noerrdialogs \
  --ozone-platform=headless \
  --ozone-override-screen-size=800,600 \
  --use-angle=swiftshader-webgl \
  about:blank > /tmp/chrome.log 2>&1 &

sleep 3
echo "[$(date)] 浏览器重启完成"
