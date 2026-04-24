# 🔄 实时数据推送实现指南

**状态**: ⏳ 待实现  
**优先级**: P0

---

## 📊 当前状态

**数据刷新方式**: 每 5 分钟自动刷新  
**问题**: 
- ❌ 无法实时推送价格变化
- ❌ 用户需要等待刷新
- ❌ 服务器资源浪费（轮询）

---

## 🎯 目标

实现 WebSocket 实时推送：
- ✅ 价格变化实时推送
- ✅ 新闻发布实时推送
- ✅ 告警触发实时推送
- ✅ 图谱数据实时更新

---

## 🏗️ 架构设计

```
┌─────────────┐      WebSocket      ┌─────────────┐
│   Browser   │ ◄─────────────────► │   Backend   │
│  (前端页面)  │                     │  (FastAPI)  │
└─────────────┘                     └──────┬──────┘
                                           │
                                    ┌──────▼──────┐
                                    │  Database   │
                                    │ (PostgreSQL)│
                                    └─────────────┘
```

---

## 🛠️ 实现方案

### 方案 1: FastAPI WebSocket (推荐) ⭐

**优点**:
- ✅ 原生支持
- ✅ 性能好
- ✅ 易于实现

**实现步骤**:

#### 1. 后端添加 WebSocket 端点

```python
# backend/websocket_manager.py
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# backend/api.py
from websocket_manager import manager

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端消息
    except:
        manager.disconnect(websocket)
```

#### 2. 价格更新时推送

```python
# backend/fetch_market_data.py
from websocket_manager import manager

async def send_price_update(symbol, price, change_percent):
    await manager.broadcast({
        "type": "price_update",
        "data": {
            "symbol": symbol,
            "price": price,
            "change_percent": change_percent
        }
    })
```

#### 3. 前端连接 WebSocket

```javascript
// frontend/index.html
let websocket = null;

function connectWebSocket() {
    websocket = new WebSocket(`ws://${window.location.host}/ws`);
    
    websocket.onopen = () => {
        console.log('✅ WebSocket 连接成功');
    };
    
    websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        if (message.type === 'price_update') {
            updatePrice(message.data);
        } else if (message.type === 'news_update') {
            addNews(message.data);
        } else if (message.type === 'alert') {
            showAlert(message.data);
        }
    };
    
    websocket.onerror = (error) => {
        console.error('❌ WebSocket 错误:', error);
    };
    
    websocket.onclose = () => {
        console.log('🔌 WebSocket 断开，5 秒后重连...');
        setTimeout(connectWebSocket, 5000);
    };
}

// 页面加载时连接
onMounted(() => {
    connectWebSocket();
});
```

---

### 方案 2: Server-Sent Events (SSE)

**优点**:
- ✅ 更简单
- ✅ 浏览器自动重连
- ✅ 单向推送足够

**缺点**:
- ❌ 仅支持单向（服务器→客户端）

**实现**:

```python
# backend/api.py
from fastapi.responses import StreamingResponse
import asyncio
import json

@app.get("/stream")
async def stream_events():
    async def event_generator():
        while True:
            # 等待新数据
            data = await get_latest_data()
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(5)  # 每 5 秒推送
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

```javascript
// frontend/index.html
const eventSource = new EventSource('/stream');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
```

---

### 方案 3: Socket.IO (最强大)

**优点**:
- ✅ 自动重连
- ✅ 房间/频道支持
- ✅ 跨浏览器兼容

**缺点**:
- ❌ 需要额外依赖

**实现**:

```python
# 后端
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('response', {'data': '连接成功'})

@socketio.on('subscribe')
def handle_subscribe(data):
    join_room(data['symbol'])
```

```javascript
// 前端
import io from 'socket.io-client';

const socket = io('http://localhost:8000');

socket.on('price_update', (data) => {
    updatePrice(data);
});

// 订阅特定股票
socket.emit('subscribe', { symbol: 'AAPL' });
```

---

## 📋 实现清单

### 后端任务

- [ ] **1. 添加 WebSocket 管理器**
  - [ ] 创建 `websocket_manager.py`
  - [ ] 实现连接管理
  - [ ] 实现广播功能

- [ ] **2. 集成到 API**
  - [ ] 添加 WebSocket 端点
  - [ ] 价格更新时推送
  - [ ] 新闻更新时推送
  - [ ] 告警触发时推送

- [ ] **3. 性能优化**
  - [ ] 连接数限制
  - [ ] 消息频率限制
  - [ ] 心跳检测

---

### 前端任务

- [ ] **1. 添加 WebSocket 连接**
  - [ ] 创建连接函数
  - [ ] 实现自动重连
  - [ ] 错误处理

- [ ] **2. 消息处理**
  - [ ] 价格更新处理
  - [ ] 新闻更新处理
  - [ ] 告警处理

- [ ] **3. UI 更新**
  - [ ] 实时价格刷新
  - [ ] 新闻列表追加
  - [ ] 告警提示显示

---

## 🎯 推荐方案

**使用方案 1 (FastAPI WebSocket)**

**理由**:
1. ✅ 原生支持，无需额外依赖
2. ✅ 双向通信，更灵活
3. ✅ 性能好，适合实时推送
4. ✅ 与现有 FastAPI 架构一致

---

## 📊 预期效果

### 当前 vs 优化后

| 指标 | 当前 | 优化后 |
|------|------|--------|
| **价格刷新** | 5 分钟轮询 | 实时推送 |
| **新闻刷新** | 5 分钟轮询 | 实时推送 |
| **告警通知** | 15 分钟检查 | 立即推送 |
| **服务器负载** | 高（频繁轮询） | 低（按需推送） |
| **用户体验** | 等待刷新 | 实时更新 |

---

## 🧪 测试计划

### 1. 功能测试
- [ ] 连接建立成功
- [ ] 价格更新推送
- [ ] 新闻更新推送
- [ ] 断线自动重连

### 2. 性能测试
- [ ] 100 个并发连接
- [ ] 消息延迟 < 100ms
- [ ] 服务器 CPU 占用 < 10%

### 3. 兼容性测试
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] 移动端浏览器

---

## 📁 文件结构

```
/root/finance-dashboard/
├── backend/
│   ├── api.py                  # 添加 WebSocket 端点
│   ├── websocket_manager.py    # 新建：连接管理
│   └── fetch_market_data.py    # 添加推送逻辑
└── frontend/
    └── index.html              # 添加 WebSocket 连接
```

---

## ⏱️ 预计时间

| 任务 | 预计时间 |
|------|---------|
| 后端 WebSocket 管理器 | 1 小时 |
| API 集成 | 1 小时 |
| 前端连接 | 1 小时 |
| 测试调试 | 1 小时 |
| **总计** | **4 小时** |

---

*创建时间：2026-03-08*  
*实施优先级：P0*
