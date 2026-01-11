
// 使用后端代理避免CORS问题
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000';

/**
 * 发送消息给 AI 助手（通过后端代理）
 * @param {string} query 用户输入
 * @param {string} userId 用户ID
 * @param {Object} userProfile 用户资料
 * @param {Function} onChunk 接收流式数据的回调
 * @param {Function} onError 错误回调
 * @param {Function} onFinish 完成回调
 */
export async function sendCozeMessage(query, userId, userProfile, onChunk, onError, onFinish) {
  try {
    // 智能后端地址：如果从网络IP访问，自动替换为当前hostname
    let apiUrl = API_BASE_URL;
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        apiUrl = API_BASE_URL.replace('localhost', hostname).replace('127.0.0.1', hostname);
      }
    }

    const response = await fetch(`${apiUrl}/api/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include', // 携带cookie
      body: JSON.stringify({
        query,
        user_id: userId || 'guest',
        user_profile: userProfile || {}
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API请求失败 (${response.status}): ${errorText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // 保留最后一个可能不完整的行

      for (const line of lines) {
        if (line.startsWith('event:')) {
            // event type - 忽略
        } else if (line.startsWith('data:')) {
            const dataStr = line.slice(5).trim();
            if (!dataStr) continue;
            try {
                const data = JSON.parse(dataStr);
                // Coze v3 stream events
                if (data.type === 'answer') {
                   onChunk(data.content);
                } else if (data.event === 'conversation.message.delta') {
                   if (data.data && data.data.content) {
                       onChunk(data.data.content);
                   }
                } else if (data.content) {
                   // 兜底：如果有content字段就显示
                   onChunk(data.content);
                }
            } catch (e) {
                console.warn('[Coze] Parse error:', e);
            }
        }
      }
    }
    
    if (onFinish) onFinish();

  } catch (error) {
    console.error('[Coze] API Error:', error);
    if (onError) onError(error);
  }
}

