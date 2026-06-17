<template>
  <div class="favorite-container">
    <van-nav-bar
      title="我的收藏"
      left-text="返回"
      left-arrow
      right-text="清空"
      fixed
      @click-left="onClickLeft"
      @click-right="onClickClear"
    />

    <div class="favorite-list" v-if="favoriteStore.getFavorites.length">
      <div class="favorite-item" v-for="item in favoriteStore.getFavorites" :key="item.id">
        <van-cell :border="false" @click="goToNewsDetail(item.id)">
          <template #title>
            <div class="news-item">
              <div class="news-image" v-if="item.image">
                <img :src="item.image" :alt="item.title">
              </div>
              <div class="news-info">
                <div class="news-title">{{ item.title }}</div>
                <div class="news-meta">
                  <span>{{ item.author }}</span>
                  <span>{{ formatTime(item.publishTime) }}</span>
                  <span>收藏时间: {{ formatTime(item.favoriteTime) }}</span>
                </div>
              </div>
            </div>
          </template>
        </van-cell>
        <van-button
          class="delete-btn"
          type="danger"
          size="mini"
          icon="cross"
          @click.stop="confirmDelete(item.id)"
        />
      </div>
    </div>

    <van-empty v-else description="暂无收藏内容" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog } from 'vant'
import { useFavoriteStore } from '../store/modules/favorite'
import { formatTime } from '../utils/formatTime'

const router = useRouter()
const favoriteStore = useFavoriteStore()

const onClickLeft = () => {
  router.back()
}

const goToNewsDetail = (id) => {
  router.push(`/news/detail/${id}`)
}

const removeFavorite = async (id) => {
  const result = await favoriteStore.removeFavoriteApi(id)
  if (result.success) {
    favoriteStore.removeFavorite(id)
  }
}

const confirmDelete = (id) => {
  showDialog({
    title: '提示',
    message: '确定要删除这条收藏吗？',
    showCancelButton: true
  }).then((action) => {
    if (action === 'confirm') {
      removeFavorite(id)
    }
  })
}

const onClickClear = async () => {
  showDialog({
    title: '提示',
    message: '确定要清空所有收藏吗？',
    showCancelButton: true
  }).then(async (action) => {
    if (action === 'confirm') {
      const result = await favoriteStore.clearFavoritesApi()
      if (!result || !result.success) {
        console.log('清空收藏列表失败')
      }
    }
  })
}

onMounted(async () => {
  try {
    const result = await favoriteStore.getFavoriteListApi()
    if (!result || !result.success) {
      favoriteStore.loadFavorites()
    }
  } catch (error) {
    favoriteStore.loadFavorites()
  }
})
</script>

<style scoped>
.favorite-container {
  padding-top: 46px;
  padding-bottom: 20px;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.favorite-list {
  padding: 10px;
}

.favorite-item {
  position: relative;
  margin-bottom: 10px;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.news-item {
  display: flex;
  padding: 10px 36px 10px 0;
}

.news-image {
  width: 120px;
  height: 80px;
  margin-right: 12px;
  flex-shrink: 0;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.news-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.news-title {
  font-size: 16px;
  font-weight: bold;
  line-height: 1.4;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.news-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 10px;
}

.delete-btn {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  z-index: 10;
  width: 24px;
  height: 24px;
  padding: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
