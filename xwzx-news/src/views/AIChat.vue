<template>
  <div class="ai-chat-container">
    <van-nav-bar title="AI问答" fixed />

    <div class="chat-content">
      <div class="messages-container" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-content">
            <div v-if="message.role === 'assistant' && message.content === ''" class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <template v-else>
              <div class="message-meta" v-if="message.role === 'assistant' && message.source">
                <span :class="['source-badge', `source-${message.source}`]">
                  {{ getSourceLabel(message.source) }}
                </span>
              </div>
              <div v-html="formatMessage(message.content)"></div>
              <div
                v-if="message.role === 'assistant' && message.news?.length"
                class="news-reference-list"
              >
                <button
                  v-for="item in message.news"
                  :key="item.id"
                  type="button"
                  class="news-reference-card"
                  @click="goToNewsDetail(item.id)"
                >
                  <div class="news-reference-image" v-if="item.image">
                    <img
                      :src="normalizeImageUrl(item.image, item.categoryId)"
                      :alt="item.title"
                      :data-category-id="item.categoryId"
                      loading="lazy"
                      @error="applyImageFallback"
                    >
                  </div>
                  <div class="news-reference-title">{{ item.title }}</div>
                  <div class="news-reference-meta">
                    <span>浏览 {{ item.views }}</span>
                    <span>{{ item.publishTime }}</span>
                  </div>
                  <div v-if="item.description" class="news-reference-description">
                    {{ item.description }}
                  </div>
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="input-container">
        <van-field
          v-model="userInput"
          rows="1"
          autosize
          type="textarea"
          placeholder="请输入问题..."
          class="chat-input"
          @keypress.enter.prevent="sendMessage"
        />
        <van-button
          type="primary"
          class="send-button"
          :disabled="isLoading || !userInput.trim()"
          @click="sendMessage"
        >
          发送
        </van-button>
      </div>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import DOMPurify from 'dompurify'
import * as marked from 'marked'
import { nextTick, onActivated, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

import TabBar from '../components/TabBar.vue'
import { useUserStore } from '../store/user'
import { applyImageFallback, normalizeImageUrl } from '../utils/imageFallback'
import request, { getErrorMessage } from '../utils/request'

const DEFAULT_MESSAGES = [
  {
    role: 'assistant',
    content: '你好，我是 AI 助手。涉及新闻排行的问题，我会优先查询当前项目数据库里的真实数据。',
    news: [],
    source: 'database',
  },
]

const messages = ref([...DEFAULT_MESSAGES])
const userInput = ref('')
const messagesContainer = ref(null)
const isLoading = ref(false)
const router = useRouter()
const userStore = useUserStore()

const formatMessage = (content) => {
  if (!content) return ''
  return DOMPurify.sanitize(marked.parse(content))
}

const getSourceLabel = (source) => {
  const sourceLabelMap = {
    ai: '模型总结',
    database: '数据库结果',
    fallback: '数据库兜底',
  }
  return sourceLabelMap[source] || '回答结果'
}

const goToNewsDetail = (id) => {
  router.push(`/news/detail/${id}`)
}

const getStorageKey = () => {
  const userId = userStore.userInfo?.id || 'guest'
  return `ai-chat-messages:${userId}`
}

const saveMessages = () => {
  localStorage.setItem(getStorageKey(), JSON.stringify(messages.value))
}

const loadMessages = () => {
  const savedMessages = localStorage.getItem(getStorageKey())
  if (!savedMessages) {
    messages.value = [...DEFAULT_MESSAGES]
    return
  }

  try {
    const parsed = JSON.parse(savedMessages)
    messages.value = Array.isArray(parsed) && parsed.length ? parsed : [...DEFAULT_MESSAGES]
  } catch {
    messages.value = [...DEFAULT_MESSAGES]
  }
}

const resetMessagesForCurrentUser = () => {
  loadMessages()
  nextTick(scrollToBottom)
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const userMessage = userInput.value.trim()
  messages.value.push({ role: 'user', content: userMessage })
  userInput.value = ''
  messages.value.push({ role: 'assistant', content: '', news: [], source: '' })

  await nextTick()
  scrollToBottom()

  isLoading.value = true
  try {
    const response = await request.post('/api/ai/chat', {
      question: userMessage,
      messages: messages.value.slice(0, -1).map((message) => ({
        role: message.role,
        content: message.content,
      })),
    })

    const assistantMessage = messages.value[messages.value.length - 1]
    assistantMessage.content =
      response.data?.data?.answer || '后端没有返回有效回答，请稍后再试。'
    assistantMessage.news = response.data?.data?.news || []
    assistantMessage.source = response.data?.data?.source || ''
    saveMessages()
  } catch (error) {
    console.error('AI chat error:', error)
    showToast('AI问答请求失败')
    const assistantMessage = messages.value[messages.value.length - 1]
    assistantMessage.content = getErrorMessage(
      error,
      'AI问答请求失败，请检查后端服务。',
    )
    assistantMessage.news = []
    assistantMessage.source = 'fallback'
    saveMessages()
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(
  messages,
  () => {
    saveMessages()
    nextTick(scrollToBottom)
  },
  { deep: true },
)

watch(
  () => userStore.userInfo?.id,
  () => {
    resetMessagesForCurrentUser()
  },
)

onMounted(() => {
  resetMessagesForCurrentUser()
})

onActivated(() => {
  resetMessagesForCurrentUser()
})
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-top: 46px;
  padding-bottom: 50px;
  box-sizing: border-box;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
  max-width: 80%;
}

.user-message {
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-content {
  padding: 10px;
  border-radius: 10px;
  word-break: break-word;
}

.message-meta {
  margin-bottom: 8px;
}

.source-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 18px;
}

.source-ai {
  background-color: #e8f3ff;
  color: #1677ff;
}

.source-database {
  background-color: #e9f8ef;
  color: #16803c;
}

.source-fallback {
  background-color: #fff3e8;
  color: #c96b16;
}

.user-message .message-content {
  background-color: #007aff;
  color: white;
}

.ai-message .message-content {
  background-color: #f2f2f2;
  color: #333;
}

.news-reference-list {
  margin-top: 12px;
  display: grid;
  gap: 8px;
}

.news-reference-card {
  width: 100%;
  border: 1px solid #e7ecf3;
  border-radius: 10px;
  background-color: #fff;
  padding: 10px;
  text-align: left;
  cursor: pointer;
}

.news-reference-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2a37;
}

.news-reference-image {
  margin-bottom: 8px;
}

.news-reference-image img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
  background-color: #eef4ff;
}

.news-reference-meta {
  margin-top: 6px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
}

.news-reference-description {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.5;
  color: #4b5563;
}

.input-container {
  display: flex;
  padding: 10px;
  border-top: 1px solid #eee;
  background-color: #fff;
}

.chat-input {
  flex: 1;
  margin-right: 10px;
}

.send-button {
  align-self: flex-end;
}

.typing-indicator {
  display: flex;
  padding: 5px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  margin: 0 2px;
  display: inline-block;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}

:deep(pre) {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

:deep(code) {
  font-family: monospace;
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 4px;
}

:deep(p) {
  margin: 8px 0;
}

:deep(ul),
:deep(ol) {
  padding-left: 20px;
}

:deep(a) {
  color: #1989fa;
  text-decoration: none;
}
</style>
