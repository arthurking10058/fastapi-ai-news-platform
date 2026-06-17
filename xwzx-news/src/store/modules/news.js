import { defineStore } from 'pinia'

import request from '../../utils/request'

const DEFAULT_CATEGORIES = [
  { id: 1, name: '头条' },
  { id: 2, name: '社会' },
  { id: 3, name: '国内' },
  { id: 4, name: '国际' },
  { id: 5, name: '娱乐' },
  { id: 6, name: '体育' },
  { id: 7, name: '科技' },
]

export const useNewsStore = defineStore('news', {
  state: () => ({
    newsList: [],
    newsDetail: {},
    categories: [...DEFAULT_CATEGORIES],
    currentCategory: 1,
    loading: false,
    refreshing: false,
    finished: false,
    categoriesLoading: false,
    detailLoading: false,
  }),

  actions: {
    async getCategories() {
      if (this.categoriesLoading) return

      this.categoriesLoading = true

      try {
        const response = await request.get('/api/news/categories')

        if (response.data?.code === 200) {
          const categories = response.data.data || []
          this.categories = [...categories, { id: 10, name: '更多' }]

          if (!this.currentCategory && categories.length > 0) {
            this.currentCategory = categories[0].id
          }
        }
      } catch (error) {
        console.error('获取新闻分类失败:', error)
        this.categories = [...DEFAULT_CATEGORIES]
        if (!this.currentCategory) {
          this.currentCategory = 1
        }
      } finally {
        this.categoriesLoading = false
      }
    },

    changeCategory(categoryId) {
      if (this.currentCategory !== categoryId) {
        this.currentCategory = categoryId
        this.newsList = []
        this.finished = false
        this.getNewsList(true)
      }
    },

    async getNewsList(isRefresh = false) {
      if (!this.currentCategory || this.loading || (!isRefresh && this.finished)) {
        return
      }

      if (isRefresh) {
        this.refreshing = true
        this.newsList = []
        this.finished = false
      }

      this.loading = true

      try {
        const params = {
          categoryId: this.currentCategory,
          page: isRefresh ? 1 : Math.ceil(this.newsList.length / 10) + 1,
          pageSize: 10,
        }

        const response = await request.get('/api/news/list', { params })

        if (response.data?.code === 200) {
          const newsData = response.data.data.list || []
          this.newsList = isRefresh ? newsData : [...this.newsList, ...newsData]
          this.finished = newsData.length < params.pageSize
        }
      } catch (error) {
        console.error('获取新闻列表失败:', error)
      } finally {
        this.loading = false
        this.refreshing = false
      }
    },

    async getNewsDetail(id) {
      if (this.detailLoading) {
        return
      }

      this.detailLoading = true
      this.newsDetail = {}

      try {
        const response = await request.get('/api/news/detail', {
          params: { id },
        })

        if (response.data?.code === 200) {
          this.newsDetail = response.data.data
        }
      } catch (error) {
        this.newsDetail = {}
        console.error('获取新闻详情失败:', error)
      } finally {
        this.detailLoading = false
      }
    },

    getCategoryName(categoryId) {
      const category = this.categories.find((item) => item.id === categoryId)
      return category ? category.name : '未知'
    },
  },
})
