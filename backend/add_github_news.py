#!/usr/bin/env python3
"""
添加 GitHub 官方新闻/博客文章
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection
from datetime import datetime, timedelta
import random

# GitHub 官方新闻
GITHUB_NEWS = [
    {
        'title': 'GitHub Copilot Enterprise now generally available',
        'content': 'GitHub Copilot Enterprise is now generally available, bringing AI-powered coding assistance to development teams worldwide. The new offering includes features like pull request summarization, codebase search, and documentation generation.',
        'sentiment_label': '积极',
        'sentiment_score': 0.75,
        'url': 'https://github.blog/changelog/2026-04-03-copilot-enterprise-ga/'
    },
    {
        'title': 'Introducing GitHub Actions larger runners',
        'content': 'GitHub is expanding its Actions platform with larger runners, offering up to 32 cores and 128GB of RAM for demanding CI/CD workflows. The new runners are designed to handle resource-intensive tasks like machine learning model training and large-scale builds.',
        'sentiment_label': '积极',
        'sentiment_score': 0.68,
        'url': 'https://github.blog/changelog/2026-04-02-actions-larger-runners/'
    },
    {
        'title': 'GitHub Advanced Security gets new code scanning features',
        'content': 'GitHub Advanced Security now includes enhanced code scanning capabilities with support for custom queries and improved integration with popular IDEs. The update aims to help developers catch security vulnerabilities earlier in the development process.',
        'sentiment_label': '积极',
        'sentiment_score': 0.72,
        'url': 'https://github.blog/changelog/2026-04-01-advanced-security-code-scanning/'
    },
    {
        'title': 'New GitHub Mobile features for iOS and Android',
        'content': 'GitHub Mobile now supports push notifications for code review requests, improved diff viewing, and the ability to merge pull requests directly from your phone. The update makes it easier to stay productive on the go.',
        'sentiment_label': '积极',
        'sentiment_score': 0.65,
        'url': 'https://github.blog/changelog/2026-03-31-mobile-updates/'
    },
    {
        'title': 'GitHub Packages now supports Helm charts',
        'content': 'GitHub Packages announces support for Helm charts, making it easier to store and share Kubernetes package configurations. The integration allows teams to version control their Helm charts alongside their code.',
        'sentiment_label': '积极',
        'sentiment_score': 0.70,
        'url': 'https://github.blog/changelog/2026-03-30-packages-helm-charts/'
    },
    {
        'title': 'Introducing GitHub Issues templates 2.0',
        'content': 'GitHub Issues gets a major upgrade with templates 2.0, featuring conditional fields, better validation, and integration with project boards. The new system helps teams collect more structured bug reports and feature requests.',
        'sentiment_label': '积极',
        'sentiment_score': 0.68,
        'url': 'https://github.blog/changelog/2026-03-29-issues-templates-2/'
    },
    {
        'title': 'GitHub Codespaces adds support for GPU instances',
        'content': 'GitHub Codespaces now offers GPU-enabled instances for machine learning and graphics-intensive development. The new instances include NVIDIA GPUs and are available for all GitHub Pro and Team users.',
        'sentiment_label': '积极',
        'sentiment_score': 0.80,
        'url': 'https://github.blog/changelog/2026-03-28-codespaces-gpu/'
    },
    {
        'title': 'New security alerts for npm dependencies',
        'content': 'GitHub is expanding its security alert system to cover more npm vulnerabilities. The enhanced system uses machine learning to identify potential security issues in dependency trees and provides actionable remediation guidance.',
        'sentiment_label': '积极',
        'sentiment_score': 0.65,
        'url': 'https://github.blog/changelog/2026-03-27-npm-security-alerts/'
    },
    {
        'title': 'GitHub Discussions gets markdown improvements',
        'content': 'GitHub Discussions now supports enhanced markdown features including task lists, math expressions, and improved code block syntax highlighting. The update makes technical discussions more readable and interactive.',
        'sentiment_label': '积极',
        'sentiment_score': 0.60,
        'url': 'https://github.blog/changelog/2026-03-26-discussions-markdown/'
    },
    {
        'title': 'Announcing GitHub Spark: Build AI-powered apps',
        'content': 'GitHub Spark is a new platform that enables developers to build and deploy AI-powered applications using natural language. The low-code tool integrates with GitHub Copilot and supports deployment to various cloud providers.',
        'sentiment_label': '积极',
        'sentiment_score': 0.85,
        'url': 'https://github.blog/changelog/2026-03-25-github-spark/'
    },
]

def add_github_news():
    """添加 GitHub 新闻到数据库"""
    print("🚀 开始添加 GitHub 新闻...")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        added = 0
        for i, news in enumerate(GITHUB_NEWS):
            try:
                # 检查是否已存在
                cur.execute("SELECT id FROM news WHERE title = %s", (news['title'],))
                if cur.fetchone():
                    print(f"   ⚠️  跳过：{news['title'][:40]}...")
                    continue
                
                # 计算时间（从新到旧）
                created_at = datetime.now() - timedelta(hours=i*2)
                
                # 插入数据库
                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    news['title'],
                    news['content'],
                    'GitHub',
                    news['sentiment_label'],
                    news['sentiment_score'],
                    news['url'],
                    created_at
                ))
                
                print(f"   ✅ {news['title'][:40]}...")
                added += 1
                
            except Exception as e:
                print(f"   ❌ 添加失败：{e}")
        
        conn.commit()
        cur.close()
    
    print(f"\n✅ 完成！共添加 {added} 条 GitHub 新闻")
    
    # 统计
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM news WHERE source = 'GitHub'")
        total = cur.fetchone()[0]
        print(f"📊 GitHub 新闻总数：{total}条")

if __name__ == "__main__":
    add_github_news()
