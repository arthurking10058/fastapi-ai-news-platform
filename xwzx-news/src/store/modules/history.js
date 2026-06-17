import { defineStore } from 'pinia'

import { useUserStore } from '../user'
import request, { getErrorMessage } from '../../utils/request'

const STORAGE_KEY = 'news_history'
const MAX_HISTORY_COUNT = 50

export const useHistoryStore = defineStore('history', {
  state: () => ({
    history: [],
    loading: false,
  }),

  getters: {
    getHistory: (state) => state.history,
  },

  actions: {
    async addHistoryApi(newsId) {
      const userStore = useUserStore()

      if (!userStore.getLoginStatus) {
        return { success: false, message: '请先登录', isLocal: true }
      }

      try {
        const response = await request.post('/api/history/add', { newsId })

        if (response.data?.code === 200) {
          return { success: true, data: response.data.data }
        }

        return {
          success: false,
          message: response.data?.message || '添加浏览历史失败',
        }
      } catch (error) {
        console.error('添加浏览历史请求失败:', error)
        return { success: false, message: getErrorMessage(error) }
      }
    },

    addHistory(news) {
      if (!news || !news.id) {
        return
      }

      const existingIndex = this.history.findIndex((item) => item.id === news.id)
      if (existingIndex !== -1) {
        this.history.splice(existingIndex, 1)
      }

      this.history.unshift({
        id: news.id,
        historyId: news.historyId,
        title: news.title,
        description: news.description,
        image: news.image,
        author: news.author,
        categoryId: news.categoryId,
        views: news.views,
        publishTime: news.publishTime,
        viewTime: new Date().toLocaleString(),
      })

      if (this.history.length > MAX_HISTORY_COUNT) {
        this.history.pop()
      }

      this.saveHistory()
    },

    mergeHistory(remoteHistory) {
      const mergedMap = new Map()
      const appendItem = (item) => {
        if (item && item.id && !mergedMap.has(item.id)) {
          mergedMap.set(item.id, item)
        }
      }

      remoteHistory.forEach(appendItem)
      this.history.forEach(appendItem)
      this.history = Array.from(mergedMap.values()).slice(0, MAX_HISTORY_COUNT)
      this.saveHistory()
    },

    clearHistory() {
      this.history = []
      this.saveHistory()
    },

    async clearHistoryApi() {
      const userStore = useUserStore()

      if (!userStore.getLoginStatus) {
        this.clearHistory()
        return { success: true, isLocal: true }
      }

      try {
        const response = await request.delete('/api/history/clear')

        if (response.data?.code === 200) {
          this.clearHistory()
          return { success: true }
        }

        return {
          success: false,
          message: response.data?.message || '清空浏览历史失败',
        }
      } catch (error) {
        console.error('清空浏览历史请求失败:', error)
        return { success: false, message: getErrorMessage(error) }
      }
    },

    removeHistory(newsId) {
      this.history = this.history.filter((item) => item.id !== newsId)
      this.saveHistory()
    },

    async removeHistoryApi(item) {
      const userStore = useUserStore()
      const newsId = typeof item === 'object' ? item.id : item
      const historyId = typeof item === 'object' ? item.historyId : null

      if (!userStore.getLoginStatus || !historyId) {
        this.removeHistory(newsId)
        return { success: true, isLocal: true }
      }

      try {
        const response = await request.delete(`/api/history/delete/${historyId}`)

        if (response.data?.code === 200) {
          this.removeHistory(newsId)
          return { success: true }
        }

        return {
          success: false,
          message: response.data?.message || '删除浏览历史失败',
        }
      } catch (error) {
        console.error('删除浏览历史请求失败:', error)
        return { success: false, message: getErrorMessage(error) }
      }
    },

    saveHistory() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.history))
    },

    loadHistory() {
      const savedHistory = localStorage.getItem(STORAGE_KEY)
      if (!savedHistory) {
        this.history = []
        return
      }

      try {
        this.history = JSON.parse(savedHistory)
      } catch (error) {
        console.error('读取本地浏览历史失败:', error)
        this.history = []
      }
    },

    async getHistoryListApi() {
      const userStore = useUserStore()
      this.loadHistory()

      if (!userStore.getLoginStatus) {
        return { success: true, data: this.history, isLocal: true }
      }

      this.loading = true

      try {
        const response = await request.get('/api/history/list')

        if (response.data?.code === 200) {
          const historyList = response.data.data.list || []
          this.mergeHistory(historyList)
          return { success: true, data: this.history }
        }

        return {
          success: false,
          message: response.data?.message || '获取浏览历史失败',
        }
      } catch (error) {
        console.error('获取浏览历史请求失败:', error)
        return { success: false, message: getErrorMessage(error) }
      } finally {
        this.loading = false
      }
    },
  },
})
