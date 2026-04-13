#!/bin/bash
# Global Insight - Vercel 部署脚本
# 使用方法：./deploy-to-vercel.sh

set -e

echo "🚀 Global Insight - Vercel 部署脚本"
echo "===================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查必要工具
check_dependencies() {
    echo "📦 检查依赖..."
    
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git 未安装${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Git 已安装${NC}"
    
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}⚠️  Vercel CLI 未安装，正在安装...${NC}"
        npm install -g vercel
    fi
    echo -e "${GREEN}✅ Vercel CLI 已安装${NC}"
    
    echo ""
}

# 初始化 Git 仓库
init_git() {
    echo "📂 初始化 Git 仓库..."
    
    cd /root/global-insight
    
    if [ ! -d ".git" ]; then
        git init
        echo -e "${GREEN}✅ Git 仓库已初始化${NC}"
    else
        echo -e "${YELLOW}⚠️  Git 仓库已存在${NC}"
    fi
    
    # 配置 Git 用户
    git config user.email "${GIT_EMAIL:-jack@example.com}"
    git config user.name "${GIT_NAME:-Jack}"
    
    # 创建 .gitignore（如果不存在）
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
.venv

# 数据库备份
*.sql
backup_*.sql.gz

# 环境配置
.env
.env.local
.env.production

# 日志
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
EOF
        echo -e "${GREEN}✅ .gitignore 已创建${NC}"
    fi
    
    echo ""
}

# 提交代码
commit_code() {
    echo "💾 提交代码..."
    
    cd /root/global-insight
    
    git add -A
    git commit -m "Deploy to Vercel - $(date '+%Y-%m-%d %H:%M')" || {
        echo -e "${YELLOW}⚠️  没有变更需要提交${NC}"
    }
    
    git branch -M main 2>/dev/null || true
    
    echo -e "${GREEN}✅ 代码已提交${NC}"
    echo ""
}

# 关联 GitHub 仓库
link_github() {
    echo "🔗 关联 GitHub 仓库..."
    
    cd /root/global-insight
    
    echo -e "${YELLOW}请输入你的 GitHub 仓库地址:${NC}"
    echo "格式：https://github.com/YOUR_USERNAME/global-insight.git"
    read -p "> " REPO_URL
    
    git remote remove origin 2>/dev/null || true
    git remote add origin "$REPO_URL"
    
    echo -e "${GREEN}✅ GitHub 仓库已关联${NC}"
    echo ""
}

# 推送到 GitHub
push_to_github() {
    echo "📤 推送到 GitHub..."
    
    cd /root/global-insight
    
    echo -e "${YELLOW}⚠️  首次推送需要使用 --force 或 -u 参数${NC}"
    git push -u origin main --force
    
    echo -e "${GREEN}✅ 代码已推送到 GitHub${NC}"
    echo ""
}

# 部署到 Vercel
deploy_vercel() {
    echo "🌐 部署到 Vercel..."
    
    cd /root/global-insight
    
    echo -e "${YELLOW}提示：如果是首次部署，Vercel 会引导你关联 GitHub 仓库${NC}"
    echo ""
    
    # 检查是否已登录
    if ! vercel whoami &>/dev/null; then
        echo -e "${YELLOW}未登录 Vercel，请先登录:${NC}"
        vercel login
    fi
    
    # 链接项目
    vercel link --repo || {
        echo -e "${YELLOW}项目未关联，将创建新项目${NC}"
    }
    
    # 部署
    echo -e "${GREEN}开始部署...${NC}"
    vercel --prod
    
    echo -e "${GREEN}✅ 部署完成！${NC}"
    echo ""
}

# 显示下一步指引
show_next_steps() {
    echo "===================================="
    echo "🎉 部署完成！"
    echo "===================================="
    echo ""
    echo "下一步操作："
    echo ""
    echo "1️⃣  配置 GitHub Secrets:"
    echo "   访问：https://github.com/YOUR_USERNAME/global-insight/settings/secrets/actions"
    echo "   添加:"
    echo "   - DATABASE_URL (你的 Neon 数据库连接字符串)"
    echo "   - DASHSCOPE_API_KEY (你的 DashScope API Key)"
    echo ""
    echo "2️⃣  配置 Vercel 环境变量:"
    echo "   访问：https://vercel.com/dashboard"
    echo "   进入你的项目 → Settings → Environment Variables"
    echo "   添加同样的环境变量"
    echo ""
    echo "3️⃣  验证部署:"
    echo "   curl https://YOUR_PROJECT.vercel.app/api/v1/health"
    echo ""
    echo "4️⃣  查看定时任务:"
    echo "   在 Vercel Dashboard → 你的项目 → Cron Jobs"
    echo ""
    echo "📚 详细文档：查看 DEPLOY_VERCEL.md 和 MIGRATE_TO_NEON.md"
    echo ""
}

# 主流程
main() {
    check_dependencies
    init_git
    commit_code
    
    echo -e "${YELLOW}是否需要关联 GitHub 仓库并推送？(y/n)${NC}"
    read -p "> " PUSH_TO_GITHUB
    
    if [ "$PUSH_TO_GITHUB" = "y" ] || [ "$PUSH_TO_GITHUB" = "Y" ]; then
        link_github
        push_to_github
    fi
    
    echo -e "${YELLOW}是否立即部署到 Vercel？(y/n)${NC}"
    read -p "> " DEPLOY_NOW
    
    if [ "$DEPLOY_NOW" = "y" ] || [ "$DEPLOY_NOW" = "Y" ]; then
        deploy_vercel
    fi
    
    show_next_steps
}

# 运行主流程
main
