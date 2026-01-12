# AI 智能旅游助手问题排查

## 问题现象
点击AI助手按钮后，无法正常对话或收不到回复。

## 原因分析

AI助手功能使用了 **Coze API**（字节跳动的AI对话平台），前端直接调用云端API。可能的问题：

### 1. CORS跨域限制（最常见）
浏览器的同源策略阻止了前端直接请求 `https://api.coze.com`

**错误信息（浏览器控制台）：**
```
Access to fetch at 'https://api.coze.com/v3/chat' from origin 'http://192.168.1.10:8080' has been blocked by CORS policy
```

**解决方案：** 需要通过后端代理转发请求

### 2. API Token 过期
Coze API Token 有有效期限制

**错误信息：**
```
API request failed with status 401
```

**解决方案：** 更新 Token（需要重新获取）

### 3. 网络连接问题
无法访问 Coze API服务器

**错误信息：**
```
Failed to fetch
NetworkError
```

**解决方案：** 检查网络连接，或使用VPN

## 完整修复方案

### 方案A：通过后端代理（推荐）

#### 步骤1：创建后端代理API

创建文件：`backend/app/routes/ai.py`

```python
from flask import Blueprint, request, jsonify, Response
import requests
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

COZE_API_URL = 'https://api.coze.com/v3/chat'
COZE_API_TOKEN = 'pat_46lwbTaFlf0a2T4ifTN7eFlNXfmpV49GyA2eAikUEdPdUr17WVlCrjpHHhTCGiS6'
BOT_ID = '7583976391813709834'

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """代理转发Coze聊天请求"""
    try:
        data = request.get_json()
        user_query = data.get('query')
        user_id = data.get('user_id', 'guest')
        user_profile = data.get('user_profile', {})
        
        # 构建消息
        messages = []
        if user_profile:
            profile_context = f"""当前用户资料：
用户名：{user_profile.get('username', '未知')}
年龄：{user_profile.get('age', '未知')}
职业：{user_profile.get('occupation', '未知')}
个人简介：{user_profile.get('bio', '无')}
请根据这些信息为用户推荐合适的旅游路线或回答问题。"""
            messages.append({
                'role': 'user',
                'content': profile_context,
                'content_type': 'text'
            })
        
        messages.append({
            'role': 'user',
            'content': user_query,
            'content_type': 'text'
        })
        
        # 调用Coze API
        resp = requests.post(
            COZE_API_URL,
            headers={
                'Authorization': f'Bearer {COZE_API_TOKEN}',
                'Content-Type': 'application/json'
            },
            json={
                'bot_id': BOT_ID,
                'user_id': user_id,
                'stream': True,
                'auto_save_history': True,
                'additional_messages': messages
            },
            stream=True
        )
        
        # 流式返回
        def generate():
            for line in resp.iter_lines():
                if line:
                    yield line + b'\n'
        
        return Response(generate(), content_type='text/event-stream')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### 步骤2：注册蓝图

修改 `backend/app/__init__.py`：

```python
# ...existing imports...
from app.routes.ai import ai_bp

def create_app():
    # ...existing code...
    
    # 注册AI路由
    app.register_blueprint(ai_bp)
    
    return app
```

#### 步骤3：修改前端API调用

修改 `frontend/src/api/coze.js`：

```javascript
import request from './index'

export async function sendCozeMessage(query, userId, userProfile, onChunk, onError, onFinish) {
  try {
    const response = await fetch('/api/ai/chat', {  // 改为后端代理
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query,
        user_id: userId || 'guest',
        user_profile: userProfile
      })
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith('data:')) {
          const dataStr = line.slice(5).trim();
          if (!dataStr) continue;
          try {
            const data = JSON.parse(dataStr);
            if (data.type === 'answer' || (data.event === 'conversation.message.delta' && data.data && data.data.content)) {
              onChunk(data.data?.content || data.content);
            }
          } catch (e) {
            console.warn('Parse error', e);
          }
        }
      }
    }
    
    if (onFinish) onFinish();

  } catch (error) {
    console.error('AI Chat Error:', error);
    if (onError) onError(error);
  }
}
```

### 方案B：使用本地AI模型（无需API）

如果不想依赖外部API，可以：

1. **使用Ollama本地部署**
   - 下载：https://ollama.com/
   - 安装模型：`ollama pull llama2`
   - 启动服务：`ollama serve`
   - 修改API调用本地地址：`http://localhost:11434/api/chat`

2. **使用OpenAI API**
   - 注册OpenAI账号
   - 获取API Key
   - 替换Coze API调用为OpenAI API

### 方案C：禁用AI功能（临时）

如果暂时不需要AI功能，可以在 `App.vue` 中注释掉：

```vue
<!-- <AiAssistant v-if="isLoggedIn" :userProfile="user" :userId="user ? user.user_id : ''" /> -->
```

## 测试步骤

1. 启动后端服务
   ```bash
   cd backend
   python app.py
   ```

2. 启动前端服务
   ```bash
   cd frontend
   npm run serve
   ```

3. 登录系统

4. 点击右下角AI助手按钮

5. 输入"你好"测试

6. 检查浏览器控制台（F12）是否有错误

## 常见错误代码

| 错误码 | 含义 | 解决方法 |
|--------|------|----------|
| 401 | Token无效或过期 | 更新COZE_API_TOKEN |
| 403 | 权限不足 | 检查BOT_ID是否正确 |
| 429 | 请求过于频繁 | 降低请求频率，添加防抖 |
| 500 | 服务器错误 | 检查后端日志 |
| CORS错误 | 跨域限制 | 使用后端代理 |

## 获取新的Coze Token

1. 访问：https://www.coze.com/
2. 登录账号
3. 进入Bot管理
4. 创建或选择Bot
5. 获取API Token
6. 更新代码中的`COZE_API_TOKEN`和`BOT_ID`

## 建议

**开发阶段：**
- 使用后端代理方案（避免CORS问题）
- 添加请求日志，方便调试

**生产环境：**
- 将Token存储在环境变量中（不要硬编码）
- 添加速率限制（防止滥用）
- 添加错误重试机制
- 考虑添加Token刷新逻辑

## 修改日期
2026-01-11
