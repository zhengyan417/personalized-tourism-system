
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
  console.log('[Coze] 开始发送消息');
  console.log('[Coze] Query:', query.substring(0, 100) + '...');
  console.log('[Coze] User ID:', userId);
  console.log('[Coze] User Profile:', userProfile);
  
  try {
    // 智能后端地址：如果从网络IP访问，自动替换为当前hostname
    let apiUrl = API_BASE_URL;
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        apiUrl = API_BASE_URL.replace('localhost', hostname).replace('127.0.0.1', hostname);
      }
    }

    console.log('[Coze] API URL:', `${apiUrl}/api/ai/chat`);

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

    console.log('[Coze] Response status:', response.status);
    console.log('[Coze] Response headers:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Coze] API Error Response:', errorText);
      throw new Error(`API请求失败 (${response.status}): ${errorText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let messageCount = 0;

    console.log('[Coze] 开始读取流式响应...');

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('[Coze] 流式响应读取完成');
        break;
      }
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // 保留最后一个可能不完整的行

      for (const line of lines) {
        if (line.startsWith('event:')) {
            const eventType = line.slice(6).trim();
            console.log('[Coze] Event:', eventType);
        } else if (line.startsWith('data:')) {
            const dataStr = line.slice(5).trim();
            if (!dataStr) continue;
            if (dataStr === '[DONE]') {
              console.log('[Coze] 收到完成标记 [DONE]');
              continue;
            }
            
            try {
                const data = JSON.parse(dataStr);
                
                // 🔍 详细打印数据结构
                console.log('[Coze] 完整数据对象:', JSON.stringify(data, null, 2).substring(0, 300));
                console.log('[Coze] 数据的所有键:', Object.keys(data));
                console.log('[Coze] type值:', data.type);
                console.log('[Coze] role值:', data.role);
                console.log('[Coze] content值长度:', data.content ? data.content.length : 0);
                console.log('[Coze] event值:', data.event);
                
                // 检查错误消息
                if (data.error) {
                   console.error('[Coze] ❌ 服务器返回错误:', data.error);
                   if (onError) {
                     onError(new Error(data.error));
                   }
                   continue;
                }
                
                // 优先处理 Coze v3 delta 事件（流式增量内容）
                if (data.event === 'conversation.message.delta' && data.data && data.data.content) {
                   console.log('[Coze] ✅ Delta 事件 - 发送内容片段');
                   messageCount++;
                   onChunk(data.data.content);
                   continue; // 🔧 处理完后跳过后续判断
                }
                
                // 跳过 completed 事件（避免重复，delta 已经包含了所有内容）
                if (data.event === 'conversation.message.completed') {
                   console.log('[Coze] ℹ️ Completed 事件 - 跳过（已通过delta接收）');
                   continue;
                }
                
                // 处理非流式的完整 answer 消息（兼容不同API版本）
                if (data.type === 'answer' && data.content && !data.event) {
                   console.log('[Coze] ✅ Answer 类型 - 发送完整内容');
                   messageCount++;
                   onChunk(data.content);
                   continue;
                }
                
                // 其他类型消息跳过
                console.log('[Coze] ❌ 跳过消息 - type:', data.type, 'event:', data.event, 'hasContent:', !!data.content);
            } catch (e) {
                console.warn('[Coze] Parse error:', e, '原始数据:', dataStr.substring(0, 100));
            }
        }
      }
    }
    
    console.log('[Coze] 总共发送了', messageCount, '个消息片段');
    
    if (onFinish) onFinish();

  } catch (error) {
    console.error('[Coze] API Error:', error);
    if (onError) onError(error);
  }
}

