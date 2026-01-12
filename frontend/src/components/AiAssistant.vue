<template>
  <div 
    class="fixed z-[1050] touch-none select-none" 
    :style="containerStyle"
    @mousedown="startDrag"
    @touchstart="startDrag"
  >
    <!-- 悬浮按钮 -->
    <div 
      class="relative cursor-pointer group"
      @click="handleClick"
      title="AI 旅游助手"
    >
      <div class="w-14 h-14 bg-gradient-to-br from-brand-500 to-brand-600 rounded-full shadow-lg flex items-center justify-center transition-transform transform group-hover:scale-110 relative z-10">
        <div class="relative">
          <i class="bi bi-stars text-yellow-300 text-sm absolute -top-2 -right-2 animate-pulse"></i>
          <i class="bi bi-robot text-2xl text-white"></i>
        </div>
      </div>
      <span class="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs font-bold text-brand-600 bg-white px-2 py-0.5 rounded-full shadow-sm opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">AI助手</span>
      <!-- 脉冲动画效果 -->
      <div class="absolute top-0 left-0 w-14 h-14 bg-brand-400 rounded-full animate-ping opacity-75 z-0"></div>
    </div>

    <!-- 聊天窗口 -->
    <div v-if="isOpen" class="absolute bottom-20 right-0 w-[350px] h-[500px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-gray-100" @mousedown.stop @touchstart.stop>
      <!-- 头部 -->
      <div class="bg-brand-600 text-white px-4 py-3 flex justify-between items-center shrink-0">
        <div class="flex items-center gap-2">
          <div class="bg-white/20 p-1.5 rounded-lg">
            <i class="bi bi-robot text-lg"></i>
          </div>
          <span class="font-bold text-sm">AI 智能旅游助手</span>
        </div>
        <button type="button" class="text-white/80 hover:text-white transition-colors" @click="toggleChat" aria-label="Close">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      
      <!-- 消息列表 -->
      <div class="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-4" ref="chatBody">
        <div v-if="messages.length === 0" class="text-center text-gray-500 mt-8">
          <div class="mb-4 inline-block bg-brand-100 p-4 rounded-full">
            <i class="bi bi-robot text-4xl text-brand-600"></i>
          </div>
          <h5 class="font-bold text-gray-800">你好！我是你的 AI 旅游助手</h5>
          <p class="mt-2 text-xs text-gray-500 px-4">我可以根据你的个人资料（{{ userProfile.age ? userProfile.age + '岁' : '' }} {{ userProfile.occupation || '' }}）<br>为你推荐专属路线。</p>
          <div class="flex flex-col gap-2 mt-6 px-6">
            <button class="text-xs bg-white border border-brand-200 text-brand-600 py-2 px-4 rounded-full hover:bg-brand-50 transition-colors shadow-sm" @click="quickAsk('推荐一个适合我的周末旅行计划')">推荐一个适合我的周末旅行计划</button>
            <button class="text-xs bg-white border border-brand-200 text-brand-600 py-2 px-4 rounded-full hover:bg-brand-50 transition-colors shadow-sm" @click="quickAsk('附近有什么好玩的景点？')">附近有什么好玩的景点？</button>
          </div>
        </div>

        <div v-for="(msg, index) in messages" :key="index" class="flex gap-2" :class="msg.role === 'user' ? 'flex-row-reverse' : ''">
          <div class="shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-xs shadow-sm" :class="msg.role === 'user' ? 'bg-gray-400' : 'bg-brand-600'">
            <i class="bi" :class="msg.role === 'user' ? 'bi-person-fill' : 'bi-robot'"></i>
          </div>
          <div class="flex flex-col gap-2 max-w-[80%]">
            <div 
              class="p-3 rounded-2xl text-sm shadow-sm" 
              :class="msg.role === 'user' ? 'bg-brand-600 text-white rounded-tr-none' : 'bg-white text-gray-700 border border-gray-100 rounded-tl-none'"
            >
              <div class="whitespace-pre-wrap break-words">{{ msg.content }}</div>
            </div>
            <!-- AI消息的操作按钮 -->
            <div v-if="msg.role === 'assistant' && msg.content && !isLoading" class="flex gap-2 px-1">
              <button 
                @click="applyToRoutePlanning(msg.content)"
                class="text-xs bg-gradient-to-r from-brand-500 to-blue-500 text-white px-3 py-1.5 rounded-lg hover:from-brand-600 hover:to-blue-600 transition-all flex items-center gap-1 shadow-sm font-medium"
                title="将AI推荐的景点应用到路径规划"
              >
                <i class="bi bi-map"></i>
                <span>应用到路径规划</span>
              </button>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="flex gap-2">
          <div class="shrink-0 w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs shadow-sm">
            <i class="bi bi-robot"></i>
          </div>
          <div class="bg-white border border-gray-100 p-3 rounded-2xl rounded-tl-none shadow-sm">
            <div class="flex gap-1">
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-100"></span>
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-200"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="p-3 bg-white border-t border-gray-100 shrink-0">
        <div class="flex gap-2">
          <input 
            type="text" 
            class="flex-1 rounded-lg border-gray-200 bg-gray-50 text-sm focus:ring-brand-500 focus:border-brand-500" 
            placeholder="输入你的问题..." 
            v-model="inputMessage"
            @keyup.enter="sendMessage"
            :disabled="isLoading"
          >
          <button class="bg-brand-600 text-white w-10 h-10 rounded-lg flex items-center justify-center hover:bg-brand-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm" type="button" @click="sendMessage" :disabled="isLoading || !inputMessage.trim()">
            <i class="bi bi-send-fill"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { sendCozeMessage } from '@/api/coze';

export default {
  name: 'AiAssistant',
  props: {
    userProfile: {
      type: Object,
      default: () => ({})
    },
    userId: {
      type: [String, Number],
      default: ''
    }
  },
  data() {
    return {
      isOpen: false,
      inputMessage: '',
      messages: [],
      isLoading: false,
      // 拖拽相关状态
      isDragging: false,
      hasDragged: false, // 区分点击和拖拽
      position: {
        right: 30,
        bottom: 30
      },
      dragOffset: { x: 0, y: 0 }
    };
  },
  computed: {
    containerStyle() {
      return {
        right: this.position.right + 'px',
        bottom: this.position.bottom + 'px',
        cursor: this.isDragging ? 'grabbing' : 'grab'
      };
    }
  },
  mounted() {
    // 监听来自个人资料页面的打开AI助手事件
    window.addEventListener('open-ai-assistant', this.handleOpenAIEvent);
  },
  beforeUnmount() {
    // 清理事件监听
    window.removeEventListener('open-ai-assistant', this.handleOpenAIEvent);
  },
  methods: {
    handleOpenAIEvent(event) {
      const { message, autoSend } = event.detail;
      
      // 打开AI助手
      if (!this.isOpen) {
        this.isOpen = true;
      }
      
      // 设置消息
      if (message) {
        this.inputMessage = message;
        
        // 如果设置了自动发送，则发送消息
        if (autoSend) {
          this.$nextTick(() => {
            this.sendMessage();
          });
        }
      }
      
      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    startDrag(e) {
      // 如果点击的是关闭按钮或聊天窗口内部，不触发拖拽
      if (e.target.closest('.ai-chat-window') || e.target.closest('.btn-close')) return;
      
      this.isDragging = true;
      this.hasDragged = false;
      
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      
      // 记录初始点击位置相对于元素的偏移
      // 这里简化处理，直接记录点击时的鼠标位置和当前的 right/bottom
      this.dragOffset.x = clientX;
      this.dragOffset.y = clientY;
      this.dragOffset.initialRight = this.position.right;
      this.dragOffset.initialBottom = this.position.bottom;

      document.addEventListener('mousemove', this.onDrag);
      document.addEventListener('mouseup', this.stopDrag);
      document.addEventListener('touchmove', this.onDrag, { passive: false });
      document.addEventListener('touchend', this.stopDrag);
    },
    onDrag(e) {
      if (!this.isDragging) return;
      e.preventDefault(); // 防止滚动
      
      this.hasDragged = true;
      
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      
      const deltaX = this.dragOffset.x - clientX; // 向左拖动，right 增加
      const deltaY = this.dragOffset.y - clientY; // 向上拖动，bottom 增加
      
      this.position.right = this.dragOffset.initialRight + deltaX;
      this.position.bottom = this.dragOffset.initialBottom + deltaY;
    },
    stopDrag() {
      this.isDragging = false;
      document.removeEventListener('mousemove', this.onDrag);
      document.removeEventListener('mouseup', this.stopDrag);
      document.removeEventListener('touchmove', this.onDrag);
      document.removeEventListener('touchend', this.stopDrag);
      
      // 边界检查，防止拖出屏幕
      const winWidth = window.innerWidth;
      const winHeight = window.innerHeight;
      
      if (this.position.right < 0) this.position.right = 0;
      if (this.position.right > winWidth - 60) this.position.right = winWidth - 60;
      if (this.position.bottom < 0) this.position.bottom = 0;
      if (this.position.bottom > winHeight - 60) this.position.bottom = winHeight - 60;
    },
    handleClick() {
      if (!this.hasDragged) {
        this.toggleChat();
      }
    },
    toggleChat() {
      this.isOpen = !this.isOpen;
      if (this.isOpen) {
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    quickAsk(text) {
      this.inputMessage = text;
      this.sendMessage();
    },
    async sendMessage() {
      const text = this.inputMessage.trim();
      if (!text) return;

      // 添加用户消息
      this.messages.push({ role: 'user', content: text });
      this.inputMessage = '';
      this.isLoading = true;
      this.scrollToBottom();

      // 调试信息：打印发送的用户资料
      console.log('[AiAssistant] 发送消息给AI');
      console.log('用户ID:', this.userId);
      console.log('用户资料:', this.userProfile);
      console.log('消息内容:', text.substring(0, 100) + (text.length > 100 ? '...' : ''));

      // 准备接收 AI 回复
      let botMsgIndex = this.messages.push({ role: 'assistant', content: '' }) - 1;

      await sendCozeMessage(
        text,
        String(this.userId || 'guest'),
        this.userProfile,
        (chunk) => {
          // 更新最后一条消息的内容
          this.messages[botMsgIndex].content += chunk;
          this.scrollToBottom();
        },
        (error) => {
          this.messages[botMsgIndex].content += '\n[出错了: 无法连接到 AI 服务]';
          this.isLoading = false;
          this.scrollToBottom();
        },
        () => {
          this.isLoading = false;
        }
      );
    },
    scrollToBottom() {
      const container = this.$refs.chatBody;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    /**
     * 将AI推荐的景点应用到路径规划
     */
    async applyToRoutePlanning(aiMessage) {
      console.log('[AI Assistant] 开始提取景点信息');
      
      // 1. 从AI消息中提取景点名称
      const attractions = this.extractAttractions(aiMessage);
      
      if (attractions.length === 0) {
        alert('未能从AI回复中识别出景点信息。请尝试询问AI推荐具体的景点。');
        return;
      }
      
      console.log('[AI Assistant] 提取到景点:', attractions);
      
      // 2. 触发全局事件，通知Home组件导入路线
      window.dispatchEvent(new CustomEvent('import-ai-route', {
        detail: {
          attractions: attractions,
          source: 'ai'
        }
      }));
      
      // 3. 不再在AI助手中显示提示，由Home组件统一处理
      console.log('[AI Assistant] 已发送导入事件到Home组件');
    },
    /**
     * 从AI消息中提取景点名称
     * 使用多种模式匹配景点信息
     */
    extractAttractions(text) {
      const attractions = [];
      const seen = new Set();
      const PLACE_SUFFIX = '(?:公园|寺|庙|塔|楼|阁|宫|殿|馆|院|山|湖|江|河|桥|城|镇|村|巷|街|胡同|广场|景区|风景区|遗址|陵|墓|故居|纪念馆|博物馆|展览馆|大道|老街|古镇|古城|步行街|大道|港|湾|峡|泉|池|谷)';
      const knownAttractions = new Set(['故宫', '天安门', '天安门广场', '长城', '八达岭长城', '颐和园', '圆明园', '北海', '北海公园', '景山', '景山公园', '天坛', '雍和宫', '什刹海', '南锣鼓巷', '王府井', '明十三陵']);

      const normalizeName = (raw) => raw
        .replace(/[“”"《》【】]/g, '')
        .replace(/（.*?）/g, '')
        .replace(/[，。,.;；\s]+$/g, '')
        .replace(/^[-•\*\d\.\s]+/, '')
        .trim();

      const tryAdd = (raw) => {
        const name = normalizeName(raw);
        if (!name || seen.has(name)) return;
        if (name.length < 2 || name.length > 20) return;
        if (new RegExp(PLACE_SUFFIX + '$').test(name) || knownAttractions.has(name)) {
          attractions.push(name);
          seen.add(name);
        }
      };

      const lines = text.split(/\r?\n+/).map(line => line.trim()).filter(Boolean);
      const dayPrefix = /^第([一二三四五六七八九十百零\d]+)(天|日)/;
      const timeRange = /^\d{1,2}:\d{2}\s*[-~到]\s*\d{1,2}:\d{2}\s*(.+)$/;

      for (const line of lines) {
        if (dayPrefix.test(line)) continue;
        const timeMatch = line.match(timeRange);
        if (timeMatch) {
          tryAdd(timeMatch[1]);
          continue;
        }
        const colonMatch = line.match(/^[^：:]+[：:]\s*(.+)$/);
        if (colonMatch) {
          tryAdd(colonMatch[1]);
          continue;
        }
        if (new RegExp(`^.{2,20}?${PLACE_SUFFIX}$`).test(line)) {
          tryAdd(line);
        }
      }

      let match;
      const pattern1 = new RegExp(`[：:]\\s*([^：:\\n,，。]+?${PLACE_SUFFIX})`, 'g');
      while ((match = pattern1.exec(text)) !== null) {
        tryAdd(match[1]);
      }

      const pattern2 = new RegExp(`[-•\\*]\\s*([^-•\\*\\n,，。]{2,20}?${PLACE_SUFFIX})`, 'g');
      while ((match = pattern2.exec(text)) !== null) {
        tryAdd(match[1]);
      }

      const pattern3 = new RegExp(`(?:前往|游览|参观|访问)\\s*([^。，,\\n]{2,20}?${PLACE_SUFFIX})`, 'g');
      while ((match = pattern3.exec(text)) !== null) {
        tryAdd(match[1]);
      }

      knownAttractions.forEach(attr => {
        if (text.includes(attr)) {
          tryAdd(attr);
        }
      });

      return attractions.slice(0, 15);
    }
  }
};
</script>

<style scoped>
.ai-assistant-container {
  position: fixed;
  z-index: 1050;
  touch-action: none; /* 防止触摸滚动 */
}

.ai-float-btn-wrapper {
  position: relative;
  width: 64px;
  height: 64px;
  cursor: pointer;
  transition: transform 0.2s;
}

.ai-float-btn-wrapper:active {
  transform: scale(0.95);
}

.ai-float-btn {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #4e54c8, #8f94fb);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.ai-icon-wrapper {
  position: relative;
  margin-top: -2px;
}

.ai-label {
  font-size: 10px;
  color: white;
  font-weight: bold;
  margin-top: -2px;
}

/* 脉冲动画 */
.ai-pulse {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(78, 84, 200, 0.6);
  z-index: 1;
  animation: pulse-animation 2s infinite;
}

@keyframes pulse-animation {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  70% {
    transform: scale(1.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

.ai-chat-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 360px;
  height: 550px;
  display: flex;
  flex-direction: column;
  border-radius: 1rem;
  overflow: hidden;
  border: none;
  /* 确保聊天窗口在左侧时不会溢出屏幕，这里简单处理，实际可能需要动态计算 */
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #4e54c8, #8f94fb);
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  font-size: 0.95rem;
  background-color: #f8f9fa !important;
}

.user-msg {
  border-bottom-right-radius: 0.25rem !important;
  background: linear-gradient(135deg, #4e54c8, #8f94fb) !important;
}

.bot-msg {
  border-bottom-left-radius: 0.25rem !important;
  background-color: white !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
}

.spinner-dots .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin: 0 2px;
  background-color: #666;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.spinner-dots .dot:nth-child(1) { animation-delay: -0.32s; }
.spinner-dots .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 移动端适配 */
@media (max-width: 576px) {
  .ai-chat-window {
    position: fixed;
    bottom: 0 !important;
    right: 0 !important;
    left: 0 !important;
    width: 100%;
    height: 70vh;
    border-radius: 1rem 1rem 0 0;
    z-index: 1060;
  }
}
</style>
