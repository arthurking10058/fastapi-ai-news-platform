import { defineStore } from 'pinia'

import { useUserStore } from '../user'
import request, { getErrorMessage } from '../../utils/request'

const FAVORITES_STORAGE_PREFIX = 'news_favorites'

export const useFavoriteStore = defineStore('favorite', {
  state: () => ({
    favorites: [],
    loading: false,
  }),

  getters: {
    getFavorites: (state) => state.favorites,
    isFavorite: (state) => (id) => state.favorites.some((item) => item.id === id),
  },

  actions: {
    getStorageKey() {
      const userStore = useUserStore()
      const userId = userStore.userInfo?.id || 'guest'
      return `${FAVORITES_STORAGE_PREFIX}:${userId}`
    },

    async checkFavoriteStatusApi(newsId) {
      const userStore = useUserStore()
      if (!userStore.getLoginStatus) {
        return {
          success: true,
          isFavorite: this.isFavorite(newsId),
          isLocal: true,
        }
      }

      try {
        this.loading = true
        const response = await request.get('/api/favorite/check', {
          params: { newsId },
        })

        if (response.data?.code === 200) {
          return {
            success: true,
            isFavorite: response.data.data.isFavorite,
          }
        }

        return {
          success: false,
          message: response.data?.message || '获取收藏状态失败',
        }
      } catch (error) {
        console.error('检查收藏状态请求失败:', error)
        return {
          success: true,
          isFavorite: this.isFavorite(newsId),
          isLocal: true,
        }
      } finally {
        this.loading = false
      }
    },

    async addFavoriteApi(newsId) {
      const userStore = useUserStore()
      if (!userStore.getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        this.loading = true
        const response = await request.post('/api/favorite/add', { newsId })

        if (response.data?.code === 200) {
          return { success: true, data: response.data.data }
        }

        return {
          success: false,
          message: response.data?.message || '收藏失败',
        }
      } catch (error) {
        console.error('添加收藏请求失败:', error)
        if (error?.response?.status === 401) {
          useUserStore().logout()
        }
        return { success: false, message: getErrorMessage(error) }
      } finally {
        this.loading = false
      }
    },

    async removeFavoriteApi(newsId) {
      const userStore = useUserStore()
      if (!userStore.getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        this.loading = true
        const response = await request.delete('/api/favorite/remove', {
          params: { newsId },
        })

        if (response.data?.code === 200) {
          return { success: true }
        }

        return {
          success: false,
          message: response.data?.message || '取消收藏失败',
        }
      } catch (error) {
        console.error('取消收藏请求失败:', error)
        if (error?.response?.status === 401) {
          useUserStore().logout()
        }
        return { success: false, message: getErrorMessage(error) }
      } finally {
        this.loading = false
      }
    },

    addFavorite(news) {
      if (!news || !news.id) {
        return
      }

      const normalizedNews = {
        ...news,
        favoriteTime: news.favoriteTime || new Date().toLocaleString(),
      }

      const existingIndex = this.favorites.findIndex((item) => item.id === news.id)
      if (existingIndex !== -1) {
        this.favorites.splice(existingIndex, 1, {
          ...this.favorites[existingIndex],
          ...normalizedNews,
        })
      } else {
        this.favorites.unshift({
          ...normalizedNews,
        })
      }

      this.saveFavorites()
    },

    removeFavorite(id) {
      this.favorites = this.favorites.filter((item) => item.id !== id)
      this.saveFavorites()
    },

    async toggleFavorite(news) {
      if (!news || !news.id) {
        console.error('无效的新闻对象:', news)
        return null
      }

      if (this.isFavorite(news.id)) {
        const result = await this.removeFavoriteApi(news.id)
        if (result.success) {
          this.removeFavorite(news.id)
          return { success: true, isFavorite: false }
        }
        console.error('取消收藏失败:', result.message)
        return { success: false, message: result.message }
      }

      const result = await this.addFavoriteApi(news.id)
      if (result.success) {
        this.addFavorite(news)
        return { success: true, isFavorite: true }
      }
      console.error('添加收藏失败:', result.message)
      return { success: false, message: result.message }
    },

    clearFavorites() {
      this.favorites = []
      this.saveFavorites()
    },

    resetFavorites() {
      this.favorites = []
    },

    async clearFavoritesApi() {
      const userStore = useUserStore()
      if (!userStore.getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        this.loading = true
        const response = await request.delete('/api/favorite/clear')

        if (response.data?.code === 200) {
          this.clearFavorites()
          return { success: true }
        }

        return {
          success: false,
          message: response.data?.message || '清空收藏失败',
        }
      } catch (error) {
        console.error('清空收藏请求失败:', error)
        if (error?.response?.status === 401) {
          useUserStore().logout()
        }
        return { success: false, message: getErrorMessage(error) }
      } finally {
        this.loading = false
      }
    },

    saveFavorites() {
      localStorage.setItem(this.getStorageKey(), JSON.stringify(this.favorites))
    },

    loadFavorites() {
      const savedFavorites = localStorage.getItem(this.getStorageKey())
      if (!savedFavorites) {
        this.favorites = []
        return
      }

      try {
        this.favorites = JSON.parse(savedFavorites)
      } catch (error) {
        console.error('读取本地收藏失败:', error)
        this.favorites = []
      }
    },

    async getFavoriteListApi(page = 1, pageSize = 10) {
      const userStore = useUserStore()
      if (!userStore.getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        this.loading = true
        const response = await request.get('/api/favorite/list', {
          params: { page, pageSize },
        })

        if (response.data?.code === 200) {
          this.favorites = response.data.data.list || []
          this.saveFavorites()
          return { success: true, data: response.data.data }
        }

        return {
          success: false,
          message: response.data?.message || '获取收藏列表失败',
        }
      } catch (error) {
        console.error('获取收藏列表请求失败:', error)
        if (error?.response?.status === 401) {
          useUserStore().logout()
        }
        return { success: false, message: getErrorMessage(error) }
      } finally {
        this.loading = false
      }
    },
  },
})
