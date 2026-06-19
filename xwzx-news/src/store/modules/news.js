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
    listRequestToken: 0,
    detailRequestToken: 0,
    newsListCache: {},
    newsDetailCache: {},
    initialLoading: false,
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
        const cached = this.newsListCache[categoryId]
        this.newsList = cached?.list || []
        this.finished = cached?.finished || false
        this.loading = false
        this.getNewsList(true)
      }
    },

    async getNewsList(isRefresh = false) {
      if (!this.currentCategory || this.loading || (!isRefresh && this.finished)) {
        return
      }

      const hasCachedList = !!this.newsListCache[this.currentCategory]?.list?.length
      if (isRefresh) {
        this.refreshing = true
        const cached = this.newsListCache[this.currentCategory]
        if (cached?.list?.length) {
          this.newsList = cached.list
          this.finished = cached.finished
        } else {
          this.newsList = []
          this.finished = false
        }
      }

      this.initialLoading = !hasCachedList && this.newsList.length === 0
      this.loading = true
      const requestToken = ++this.listRequestToken

      try {
        const params = {
          categoryId: this.currentCategory,
          page: isRefresh ? 1 : Math.ceil(this.newsList.length / 10) + 1,
          pageSize: 10,
        }

        const response = await request.get('/api/news/list', { params })

        if (requestToken !== this.listRequestToken) {
          return
        }

        if (response.data?.code === 200) {
          const newsData = response.data.data.list || []
          this.newsList = isRefresh ? newsData : [...this.newsList, ...newsData]
          this.finished = newsData.length < params.pageSize
          this.newsListCache[this.currentCategory] = {
            list: [...this.newsList],
            finished: this.finished,
          }
        }
      } catch (error) {
        if (requestToken !== this.listRequestToken) {
          return
        }
        console.error('获取新闻列表失败:', error)
      } finally {
        if (requestToken === this.listRequestToken) {
          this.loading = false
          this.refreshing = false
          this.initialLoading = false
        }
      }
    },

    async prefetchFirstPage(categoryId) {
      if (!categoryId || this.newsListCache[categoryId]?.list?.length) {
        return
      }

      try {
        const response = await request.get('/api/news/list', {
          params: {
            categoryId,
            page: 1,
            pageSize: 10,
          },
        })

        if (response.data?.code === 200) {
          const newsData = response.data.data.list || []
          this.newsListCache[categoryId] = {
            list: newsData,
            finished: newsData.length < 10,
          }
        }
      } catch (error) {
        console.error('预取新闻列表失败:', error)
      }
    },

    async getNewsDetail(id) {
      if (this.detailLoading) {
        this.detailRequestToken += 1
      }

      const requestToken = ++this.detailRequestToken
      this.detailLoading = true
      this.newsDetail = this.newsDetailCache[id] || {}

      try {
        const response = await request.get('/api/news/detail', {
          params: { id },
        })

        if (requestToken !== this.detailRequestToken) {
          return null
        }

        if (response.data?.code === 200) {
          this.newsDetail = response.data.data
          this.newsDetailCache[id] = response.data.data
          return this.newsDetail
        }
      } catch (error) {
        if (requestToken === this.detailRequestToken) {
          this.newsDetail = {}
        }
        console.error('获取新闻详情失败:', error)
      } finally {
        if (requestToken === this.detailRequestToken) {
          this.detailLoading = false
        }
      }

      return null
    },

    getCategoryName(categoryId) {
      const category = this.categories.find((item) => item.id === categoryId)
      return category ? category.name : '未知'
    },
  },
})
