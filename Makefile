# Global Insight Makefile
# 快速命令参考

.PHONY: help format lint test clean deploy monitor logs benchmark

help:
	@echo "Global Insight 项目命令:"
	@echo "  make format    - 格式化代码 (black + isort)"
	@echo "  make lint      - 代码检查 (flake8)"
	@echo "  make test      - 运行性能测试"
	@echo "  make clean     - 清理缓存文件"
	@echo "  make benchmark - 性能基准测试"
	@echo "  make monitor   - 运行监控检查"
	@echo "  make logs      - 查看日志"

format:
	@echo "🎨 格式化代码..."
	pip install black isort >/dev/null 2>&1 || true
	black backend/ --exclude='venv|archive' 2>/dev/null || true
	isort backend/ --skip=venv --skip=archive 2>/dev/null || true
	@echo "✅ 格式化完成"

lint:
	@echo "🔍 代码检查..."
	pip install flake8 >/dev/null 2>&1 || true
	flake8 backend/ --exclude=venv,archive 2>/dev/null || true
	@echo "✅ 检查完成"

test: benchmark

clean:
	@echo "🧹 清理缓存..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ 清理完成"

benchmark:
	@echo "🚀 性能测试..."
	docker exec global-insight-backend python3 /app/benchmark.py

monitor:
	@echo "🔍 运行监控..."
	docker exec global-insight-backend python3 /app/monitor.py

logs:
	@echo "📋 查看日志..."
	tail -f /var/log/global-insight/*.log

deploy:
	@echo "🚀 重新部署..."
	cd /root/global-insight && docker-compose up -d --build
	@echo "✅ 部署完成"
