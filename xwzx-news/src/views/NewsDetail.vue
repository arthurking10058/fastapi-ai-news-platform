<template>
  <div class="news-detail">
    <van-nav-bar
      title="新闻详情"
      left-text="返回"
      left-arrow
      fixed
      @click-left="onClickLeft"
    />

    <div class="detail-content" v-if="newsStore.newsDetail.id">
      <div class="title-container">
        <h1 class="title">{{ newsStore.newsDetail.title }}</h1>
        <van-button
          class="favorite-btn"
          :icon="isFavorite ? 'star' : 'star-o'"
          :class="{ 'is-favorite': isFavorite }"
          @click="toggleFavorite"
        />
      </div>

      <div class="info">
        <span>{{ newsStore.newsDetail.author }}</span>
        <span>{{ formatTime(newsStore.newsDetail.publishTime) }}</span>
        <span>{{ newsStore.newsDetail.views }} 阅读</span>
      </div>

      <div class="cover" v-if="newsStore.newsDetail.image">
        <img :src="newsStore.newsDetail.image" :alt="newsStore.newsDetail.title">
      </div>

      <div class="content">
        <p v-for="(paragraph, index) in contentParagraphs" :key="index">
          {{ paragraph }}
        </p>
      </div>

      <div class="related-news" v-if="newsStore.newsDetail.relatedNews?.length">
        <h3>相关推荐</h3>
        <div class="related-list">
          <div
            class="related-item"
            v-for="item in newsStore.newsDetail.relatedNews"
            :key="item.id"
            @click="goToRelatedNews(item.id)"
          >
            <div class="related-image" v-if="item.image">
              <img :src="item.image" :alt="item.title">
            </div>
            <div class="related-title">{{ item.title }}</div>
          </div>
        </div>
      </div>
    </div>

    <van-empty v-else description="加载中..." />
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useNewsStore } from '../store/modules/news'
import { useHistoryStore } from '../store/modules/history'
import { useFavoriteStore } from '../store/modules/favorite'
import { useUserStore } from '../store/user'
import { formatTime } from '../utils/formatTime'

const route = useRoute()
const router = useRouter()
const newsStore = useNewsStore()
const historyStore = useHistoryStore()
const favoriteStore = useFavoriteStore()
const userStore = useUserStore()

const newsId = computed(() => Number(route.params.id))

const contentParagraphs = computed(() => {
  if (!newsStore.newsDetail.content) return []
  return newsStore.newsDetail.content.split('\n\n').filter(p => p.trim())
})

const isFavorite = computed(() => favoriteStore.isFavorite(newsId.value))

const onClickLeft = () => {
  router.back()
}

const goToRelatedNews = (id) => {
  router.push(`/news/detail/${id}`)
}

const recordHistory = async () => {
  if (!newsStore.newsDetail.id) {
    return
  }

  historyStore.addHistory(newsStore.newsDetail)

  if (userStore.getLoginStatus) {
    historyStore.addHistoryApi(newsStore.newsDetail.id)
  }
}

const toggleFavorite = async () => {
  if (!userStore.getLoginStatus) {
    showToast({
      message: '请先登录后再收藏',
      position: 'bottom'
    })
    router.push('/login')
    return
  }

  const status = await favoriteStore.toggleFavorite(newsStore.newsDetail)

  if (status === true) {
    showToast({
      message: '已添加到收藏',
      position: 'bottom'
    })
  } else if (status === false) {
    showToast({
      message: '已取消收藏',
      position: 'bottom'
    })
  } else {
    showToast({
      message: '操作失败，请稍后重试',
      position: 'bottom'
    })
  }
}

const loadDetail = async () => {
  await newsStore.getNewsDetail(newsId.value)
  await recordHistory()

  favoriteStore.loadFavorites()

  if (userStore.getLoginStatus && newsStore.newsDetail.id) {
    const result = await favoriteStore.checkFavoriteStatusApi(newsStore.newsDetail.id)
    if (result.success && !result.isLocal) {
      if (result.isFavorite && !favoriteStore.isFavorite(newsStore.newsDetail.id)) {
        favoriteStore.addFavorite(newsStore.newsDetail)
      } else if (!result.isFavorite && favoriteStore.isFavorite(newsStore.newsDetail.id)) {
        favoriteStore.removeFavorite(newsStore.newsDetail.id)
      }
    }
  }
}

onMounted(loadDetail)

watch(newsId, () => {
  loadDetail()
})
</script>

<style scoped>
.news-detail {
  padding-top: 46px;
  background-color: #fff;
  min-height: 100vh;
}

.detail-content {
  padding: 16px;
}

.title-container {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}

.title {
  font-size: 22px;
  font-weight: bold;
  line-height: 1.4;
  margin: 0;
  flex: 1;
}

.favorite-btn {
  flex-shrink: 0;
  margin-left: 10px;
  padding: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.favorite-btn.is-favorite {
  color: #ff9500;
}

.info {
  display: flex;
  font-size: 12px;
  color: #999;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 4px 12px;
}

.cover {
  margin-bottom: 16px;
}

.cover img {
  width: 100%;
  border-radius: 4px;
}

.content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.content p {
  margin-bottom: 16px;
  text-align: justify;
}

.related-news {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 8px solid #f5f5f5;
}

.related-news h3 {
  font-size: 18px;
  margin: 0 0 16px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  align-items: center;
}

.related-image {
  width: 80px;
  height: 60px;
  margin-right: 12px;
  flex-shrink: 0;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.related-title {
  font-size: 14px;
  line-height: 1.4;
  flex: 1;
}
</style>
