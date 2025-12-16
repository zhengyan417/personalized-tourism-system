
const COZE_API_URL = 'https://api.coze.com/v3/chat';
const COZE_API_TOKEN = 'pat_46lwbTaFlf0a2T4ifTN7eFlNXfmpV49GyA2eAikUEdPdUr17WVlCrjpHHhTCGiS';
const BOT_ID = '7583976391813709834';

/**
 * 发送消息给 Coze Bot
 * @param {string} query 用户输入
 * @param {string} userId 用户ID
 * @param {Array} history 历史消息 (Coze v3 auto_save_history=true 时可能不需要手动传，但为了上下文可以传 additional_messages)
 * @param {Function} onChunk 接收流式数据的回调
 * @param {Function} onError 错误回调
 * @param {Function} onFinish 完成回调
 */
export async function sendCozeMessage(query, userId, userProfile, onChunk, onError, onFinish) {
  try {
    const messages = [];
    
    // 如果有用户信息，作为上下文添加到消息中
    if (userProfile) {
      const profileContext = `当前用户资料：
用户名：${userProfile.username || '未知'}
年龄：${userProfile.age || '未知'}
职业：${userProfile.occupation || '未知'}
个人简介：${userProfile.bio || '无'}
请根据这些信息为用户推荐合适的旅游路线或回答问题。`;
      
      messages.push({
        role: 'user',
        content: profileContext,
        content_type: 'text'
      });
    }

    messages.push({
      role: 'user',
      content: query,
      content_type: 'text'
    });

    const response = await fetch(COZE_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${COZE_API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        bot_id: BOT_ID,
        user_id: userId || 'guest',
        stream: true,
        auto_save_history: true,
        additional_messages: messages
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
      buffer = lines.pop(); // 保留最后一个可能不完整的行

      for (const line of lines) {
        if (line.startsWith('event:')) {
            // event type
        } else if (line.startsWith('data:')) {
            const dataStr = line.slice(5).trim();
            if (!dataStr) continue;
            try {
                const data = JSON.parse(dataStr);
                // Coze v3 stream events: conversation.message.delta, conversation.message.completed, etc.
                if (data.type === 'answer' || (data.type === 'conversation.message.delta' && data.content)) {
                   onChunk(data.content);
                } else if (data.event === 'conversation.message.delta') {
                   // v3 format check
                   if (data.data && data.data.content) {
                       onChunk(data.data.content);
                   }
                }
            } catch (e) {
                console.warn('Parse error', e);
            }
        }
      }
    }
    
    if (onFinish) onFinish();

  } catch (error) {
    console.error('Coze API Error:', error);
    if (onError) onError(error);
  }
}
