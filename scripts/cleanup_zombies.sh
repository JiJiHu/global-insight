#!/bin/bash
# 清理 Chrome 僵尸进程
echo "[$(date)] 清理僵尸进程..."

# 查找并清理僵尸进程
ps aux | grep "chrome.*defunct" | grep -v grep | awk '{print $2}' | while read pid; do
    # 僵尸进程无法直接 kill，需要清理父进程
    ppid=$(ps -o ppid= -p $pid 2>/dev/null || echo "")
    if [ -n "$ppid" ] && [ "$ppid" != "1" ]; then
        echo "  清理父进程：$ppid"
        kill -9 $ppid 2>/dev/null || true
    fi
done

# 清理超过 24 小时的 Chrome 进程
ps aux | grep "chrome" | grep -v grep | awk '{if ($10 > 86400) print $2}' | while read pid; do
    echo "  清理超时进程：$pid"
    kill -9 $pid 2>/dev/null || true
done

echo "[$(date)] 清理完成"
