#!/bin/bash
# Global Insight 管理脚本

set -e

COMMAND=$1
shift || true

case "$COMMAND" in
  status)
    echo "📊 Global Insight 状态检查"
    echo "================================"
    docker ps --filter "name=global-insight" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "📈 数据库统计:"
    docker exec global-insight-backend python3 -c "
from db import get_db_connection
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM news')
    print(f'  新闻：{cur.fetchone()[0]} 条')
    cur.execute('SELECT COUNT(*) FROM market_data')
    print(f'  市场：{cur.fetchone()[0]} 条')
"
    ;;
  
  restart)
    echo "🔄 重启服务..."
    cd /root/global-insight && docker-compose restart
    echo "✅ 重启完成"
    ;;
  
  rebuild)
    echo "🔨 重新构建..."
    cd /root/global-insight && docker-compose up -d --build
    echo "✅ 构建完成"
    ;;
  
  logs)
    docker logs -f global-insight-${1:-backend}
    ;;
  
  backup)
    echo "💾 备份数据库..."
    BACKUP_FILE="/root/global-insight/backups/db_$(date +%Y%m%d_%H%M%S).sql"
    mkdir -p /root/global-insight/backups
    docker exec global-insight-db pg_dump -U jack finance_insight > "$BACKUP_FILE"
    echo "✅ 备份完成：$BACKUP_FILE"
    ;;
  
  clean)
    echo "🧹 清理 Docker 资源..."
    docker system prune -f
    echo "✅ 清理完成"
    ;;
  
  *)
    echo "用法：$0 {status|restart|rebuild|logs|backup|clean}"
    echo ""
    echo "命令说明:"
    echo "  status  - 查看服务状态"
    echo "  restart - 重启服务"
    echo "  rebuild - 重新构建"
    echo "  logs    - 查看日志 (backend|frontend|db)"
    echo "  backup  - 备份数据库"
    echo "  clean   - 清理 Docker 资源"
    exit 1
    ;;
esac
