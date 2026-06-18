import { defineStore } from 'pinia'

import { useFavoriteStore } from './modules/favorite'
import { useHistoryStore } from './modules/history'
import request, { getErrorMessage } from '../utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: '',
    isLogin: false,
    userBio: '这是我的个人简介',
  }),

  getters: {
    getUserInfo: (state) => state.userInfo,
    getToken: (state) => state.token,
    getLoginStatus: (state) => state.isLogin,
    getUserBio: (state) => state.userInfo?.bio || state.userBio,
  },

  actions: {
    syncUserScopedData() {
      const favoriteStore = useFavoriteStore()
      const historyStore = useHistoryStore()
      favoriteStore.resetFavorites()
      historyStore.resetHistory()
      favoriteStore.loadFavorites()
      historyStore.loadHistory()
    },

    async login(userData) {
      try {
        const response = await request.post('/api/user/login', {
          username: userData.username,
          password: userData.password,
        })

        if (response.data?.code === 200) {
          const userInfo = response.data.data.userInfo
          const token = response.data.data.token

          this.userInfo = userInfo
          this.token = token
          this.isLogin = true
          this.syncUserScopedData()

          return { success: true, message: '登录成功' }
        }

        return {
          success: false,
          message: response.data?.message || '登录失败',
        }
      } catch (error) {
        console.error('登录请求失败:', error)
        return { success: false, message: getErrorMessage(error, '登录请求失败，请稍后再试') }
      }
    },

    async register(userData) {
      try {
        const response = await request.post('/api/user/register', {
          username: userData.username,
          password: userData.password,
        })

        if (response.data?.code === 200) {
          const userInfo = response.data.data.userInfo
          const token = response.data.data.token

          this.userInfo = userInfo
          this.token = token
          this.isLogin = true
          this.syncUserScopedData()

          return { success: true, message: '注册成功' }
        }

        return {
          success: false,
          message: response.data?.message || '注册失败',
        }
      } catch (error) {
        console.error('注册请求失败:', error)
        return { success: false, message: getErrorMessage(error, '注册请求失败，请稍后再试') }
      }
    },

    logout() {
      const favoriteStore = useFavoriteStore()
      const historyStore = useHistoryStore()
      favoriteStore.resetFavorites()
      historyStore.resetHistory()
      this.userInfo = null
      this.token = ''
      this.isLogin = false
      favoriteStore.loadFavorites()
      historyStore.loadHistory()
    },

    async getUserInfoDetail() {
      if (!this.token) {
        return { success: false, message: '未登录' }
      }

      try {
        const response = await request.get('/api/user/info')

        if (response.data?.code === 200) {
          this.userInfo = response.data.data
          return {
            success: true,
            message: '获取用户信息成功',
            data: response.data.data,
          }
        }

        return {
          success: false,
          message: response.data?.message || '获取用户信息失败',
        }
      } catch (error) {
        console.error('获取用户信息请求失败:', error)
        return { success: false, message: getErrorMessage(error, '获取用户信息请求失败，请稍后再试') }
      }
    },

    async updateUserBio(bio) {
      if (!this.token) {
        return { success: false, message: '未登录' }
      }

      try {
        const response = await request.put('/api/user/update', { bio })

        if (response.data?.code === 200) {
          this.userInfo = {
            ...this.userInfo,
            bio,
          }
          return { success: true, message: '更新个人简介成功' }
        }

        return {
          success: false,
          message: response.data?.message || '更新个人简介失败',
        }
      } catch (error) {
        console.error('更新个人简介请求失败:', error)
        return { success: false, message: getErrorMessage(error, '更新个人简介请求失败，请稍后再试') }
      }
    },

    async updatePassword(oldPassword, newPassword) {
      if (!this.token) {
        return { success: false, message: '未登录' }
      }

      try {
        const response = await request.put('/api/user/password', {
          oldPassword,
          newPassword,
        })

        if (response.data?.code === 200) {
          return { success: true, message: '密码修改成功' }
        }

        return {
          success: false,
          message: response.data?.message || '密码修改失败',
        }
      } catch (error) {
        console.error('修改密码请求失败:', error)
        return { success: false, message: getErrorMessage(error, '修改密码请求失败，请稍后再试') }
      }
    },
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'user-store',
        storage: localStorage,
      },
    ],
  },
})
