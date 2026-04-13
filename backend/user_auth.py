#!/usr/bin/env python3
"""
简单用户认证模块
- JWT Token 认证
- 用户注册/登录
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

# 简单用户数据库（生产环境应用 PostgreSQL）
USERS_DB = {
    'jack': {
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'created_at': '2026-03-01'
    }
}

# Token 存储（生产环境应用 Redis）
TOKENS_DB = {}

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(username: str) -> str:
    """生成 Token"""
    token = secrets.token_urlsafe(32)
    TOKENS_DB[token] = {
        'username': username,
        'expires_at': datetime.now() + timedelta(days=7)
    }
    return token

def verify_token(token: str) -> Optional[str]:
    """验证 Token"""
    if token not in TOKENS_DB:
        return None
    
    token_data = TOKENS_DB[token]
    if datetime.now() > token_data['expires_at']:
        del TOKENS_DB[token]
        return None
    
    return token_data['username']

def authenticate_user(username: str, password: str) -> bool:
    """认证用户"""
    if username not in USERS_DB:
        return False
    
    user = USERS_DB[username]
    password_hash = hash_password(password)
    
    return user['password_hash'] == password_hash

def register_user(username: str, password: str) -> bool:
    """注册用户"""
    if username in USERS_DB:
        return False
    
    USERS_DB[username] = {
        'password_hash': hash_password(password),
        'role': 'user',
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }
    return True

# 测试
if __name__ == '__main__':
    print("🔐 测试用户认证模块...")
    
    # 测试登录
    print("\n1️⃣ 测试登录:")
    result = authenticate_user('jack', 'admin123')
    print(f"   jack/admin123: {'✅ 成功' if result else '❌ 失败'}")
    
    # 测试 Token
    print("\n2️⃣ 测试 Token:")
    token = generate_token('jack')
    print(f"   生成 Token: {token[:20]}...")
    username = verify_token(token)
    print(f"   验证 Token: {'✅ 成功' if username else '❌ 失败'} (用户：{username})")
    
    # 测试注册
    print("\n3️⃣ 测试注册:")
    result = register_user('test', 'test123')
    print(f"   注册 test 用户：{'✅ 成功' if result else '❌ 失败'}")
    
    print("\n✅ 测试完成")
