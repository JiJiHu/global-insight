#!/bin/bash
# Global Insight - 执行清理旧服务残留
# ⚠️ 警告：此脚本会删除旧的服务数据，请谨慎执行

set -e

echo "⚠️  警告：即将清理旧的服务残留"
echo "======================================"
echo ""
echo "此操作将删除:"
echo "  - 旧的 Docker 容器 (finance-*)"
echo "  - 旧的 Docker 镜像 (finance-*)"
echo "  - 旧的 Docker 网络 (finance-*)"
echo "  - 旧的定时任务 (finance-dashboard)"
echo "  - 旧的日志文件 (/var/log/finance*)"
echo ""
read -p "确认继续？(yes/no): " -r
echo ""
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ 取消操作"
    exit 1
fi

CLEANED=0

# 1. 停止并删除旧容器
echo "1️⃣  清理旧容器..."
for container in $(docker ps -a --format '{{.Names}}' | grep -E "^finance-" || true); do
    echo "   停止并删除：$container"
    docker stop "$container" 2>/dev/null || true
    docker rm "$container" 2>/dev/null || true
    CLEANED=$((CLEANED+1))
done
echo "   ✅ 容器清理完成"
echo ""

# 2. 删除旧镜像
echo "2️⃣  清理旧镜像..."
for image in $(docker images --format '{{.ID}} {{.Repository}}' | grep -E "^finance-" | awk '{print $1}' || true); do
    echo "   删除镜像：$image"
    docker rmi "$image" 2>/dev/null || true
    CLEANED=$((CLEANED+1))
done
echo "   ✅ 镜像清理完成"
echo ""

# 3. 清理定时任务
echo "3️⃣  清理旧定时任务..."
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null | grep -v "/root/finance-dashboard/" > "$TEMP_CRON" || true
crontab "$TEMP_CRON" 2>/dev/null || true
rm -f "$TEMP_CRON"
echo "   ✅ 定时任务清理完成"
echo ""

# 4. 删除旧网络
echo "4️⃣  清理旧网络..."
for network in $(docker network ls --format '{{.Name}}' | grep -E "^finance-" || true); do
    echo "   删除网络：$network"
    docker network rm "$network" 2>/dev/null || true
    CLEANED=$((CLEANED+1))
done
echo "   ✅ 网络清理完成"
echo ""

# 5. 清理旧日志
echo "5️⃣  清理旧日志..."
if [ -d "/var/log/finance" ]; then
    echo "   删除目录：/var/log/finance"
    rm -rf "/var/log/finance"
    CLEANED=$((CLEANED+1))
fi
for logfile in /var/log/finance*.log; do
    if [ -f "$logfile" ]; then
        echo "   删除文件：$logfile"
        rm -f "$logfile"
        CLEANED=$((CLEANED+1))
    fi
done
echo "   ✅ 日志清理完成"
echo ""

# 6. 可选：删除旧项目目录（需要用户确认）
echo "6️⃣  旧项目目录处理..."
if [ -d "/root/finance-dashboard" ]; then
    echo "   发现目录：/root/finance-dashboard"
    read -p "   是否删除此目录？(建议先备份，yes/no): " -r
    echo ""
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "   删除目录：/root/finance-dashboard"
        rm -rf "/root/finance-dashboard"
        CLEANED=$((CLEANED+1))
        echo "   ✅ 目录已删除"
    else
        echo "   ⚠️  保留目录，请手动处理"
    fi
else
    echo "   ✅ 无旧项目目录"
fi
echo ""

echo "======================================"
echo "✅ 清理完成！共清理 ${CLEANED} 项"
echo ""
echo "📋 当前运行状态验证:"
echo ""
echo "运行中的容器:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep global-insight
echo ""
echo "当前定时任务:"
crontab -l 2>/dev/null | grep global-insight || echo "无 global-insight 定时任务"
echo ""
echo "💡 建议："
echo "   1. 访问 http://150.40.177.181:11279 验证服务正常"
echo "   2. 检查日志：tail -f /var/log/global-insight/market.log"
echo "   3. 等待 10 分钟确认定时任务正常执行"
