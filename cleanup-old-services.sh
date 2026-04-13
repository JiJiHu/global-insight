#!/bin/bash
# Global Insight - 清理旧服务残留脚本
# 执行前请确认：所有重要数据已备份，新服务运行正常

set -e

echo "🔍 Global Insight 旧服务残留清理检查"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查项统计
TOTAL=0
CLEANED=0
SKIPPED=0

echo "📋 检查清单:"
echo ""

# 1. 检查旧的 Docker 容器
echo "1️⃣  Docker 容器检查"
OLD_CONTAINERS=$(docker ps -a --format '{{.Names}}' | grep -E "^finance-" || true)
if [ -n "$OLD_CONTAINERS" ]; then
    echo -e "   ${YELLOW}⚠️  发现旧的容器:${NC}"
    echo "$OLD_CONTAINERS" | sed 's/^/      /'
    TOTAL=$((TOTAL+1))
else
    echo -e "   ${GREEN}✅ 无旧容器${NC}"
fi
echo ""

# 2. 检查旧的 Docker 镜像
echo "2️⃣  Docker 镜像检查"
OLD_IMAGES=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep -E "^finance-" || true)
if [ -n "$OLD_IMAGES" ]; then
    echo -e "   ${YELLOW}⚠️  发现旧的镜像:${NC}"
    echo "$OLD_IMAGES" | sed 's/^/      /'
    TOTAL=$((TOTAL+1))
else
    echo -e "   ${GREEN}✅ 无旧镜像${NC}"
fi
echo ""

# 3. 检查定时任务
echo "3️⃣  定时任务检查"
OLD_CRONS=$(crontab -l 2>/dev/null | grep "/root/finance-dashboard/" || true)
if [ -n "$OLD_CRONS" ]; then
    echo -e "   ${YELLOW}⚠️  发现旧的定时任务:${NC}"
    echo "$OLD_CRONS" | sed 's/^/      /'
    TOTAL=$((TOTAL+1))
else
    echo -e "   ${GREEN}✅ 无旧定时任务${NC}"
fi
echo ""

# 4. 检查 Docker 网络
echo "4️⃣  Docker 网络检查"
OLD_NETWORKS=$(docker network ls --format '{{.Name}}' | grep -E "^finance-" || true)
if [ -n "$OLD_NETWORKS" ]; then
    echo -e "   ${YELLOW}⚠️  发现旧的网络:${NC}"
    echo "$OLD_NETWORKS" | sed 's/^/      /'
    TOTAL=$((TOTAL+1))
else
    echo -e "   ${GREEN}✅ 无旧网络${NC}"
fi
echo ""

# 5. 检查日志目录
echo "5️⃣  日志文件检查"
if [ -d "/var/log/finance" ] || ls /var/log/finance*.log 1>/dev/null 2>&1; then
    echo -e "   ${YELLOW}⚠️  发现旧的日志文件:${NC}"
    [ -d "/var/log/finance" ] && echo "      /var/log/finance/"
    ls /var/log/finance*.log 2>/dev/null | sed 's/^/      /'
    TOTAL=$((TOTAL+1))
else
    echo -e "   ${GREEN}✅ 无旧日志${NC}"
fi
echo ""

# 6. 检查旧的项目目录
echo "6️⃣  项目目录检查"
if [ -d "/root/finance-dashboard" ]; then
    echo -e "   ${YELLOW}⚠️  发现旧的项目目录:${NC}"
    echo "      /root/finance-dashboard/"
    TOTAL=$((TOTAL+1))
else
    echo -e "   ${GREEN}✅ 无旧目录${NC}"
fi
echo ""

echo "======================================"
echo "📊 检查总结:"
echo "   发现 ${TOTAL} 项需要清理"
echo ""

if [ $TOTAL -eq 0 ]; then
    echo -e "${GREEN}✅ 系统已完全清理，无旧服务残留！${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  发现旧服务残留，建议清理${NC}"
    echo ""
    echo "💡 执行清理命令:"
    echo "   sudo bash $0 --clean"
    echo ""
fi
