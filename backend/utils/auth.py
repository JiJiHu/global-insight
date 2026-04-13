#!/usr/bin/env python3
"""
API 认证模块
支持 Token 验证和权限控制
"""
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
import os
import hashlib
import time

# 配置
API_TOKEN = os.getenv('GLOBAL_INSIGHT_API_TOKEN', 'demo-token-123456')  # 生产环境请修改
TOKEN_FILE = '/app/.api_token'

# HTTP Bearer Token
security = HTTPBearer(auto_error=False)

def verify_token(token: str) -> bool:
    """验证 Token"""
    if not token:
        return False
    return token == API_TOKEN

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """获取当前用户（从 Token）"""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    if not verify_token(token):
        raise HTTPException(
            status_code=401,
            detail="无效的 Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return "api_user"

def require_auth(func):
    """认证装饰器（用于普通函数）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 简单实现，实际使用 FastAPI Depends
        token = kwargs.get('token')
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="认证失败")
        return func(*args, **kwargs)
    return wrapper

def generate_token() -> str:
    """生成新的 API Token"""
    import secrets
    token = f"gi_{secrets.token_urlsafe(32)}"
    
    # 保存到文件
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)
    
    return token

def get_token() -> str:
    """获取当前 Token"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return API_TOKEN

if __name__ == "__main__":
    # 生成新 Token
    new_token = generate_token()
    print(f"🔑 新的 API Token: {new_token}")
    print(f"💾 已保存到：{TOKEN_FILE}")
    print("\n使用示例:")
    print(f'  curl -H "Authorization: Bearer {new_token}" http://localhost:8000/api/v1/health')
