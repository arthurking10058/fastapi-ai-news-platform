<template>
  <div class="history-container">
    <van-nav-bar
      title="浏览历史"
      left-text="返回"
      left-arrow
      right-text="清空"
      fixed
      @click-left="onClickLeft"
      @click-right="onClickClear"
    />

    <div class="history-list" v-if="historyStore.getHistory.length">
      <div
        class="history-item"
        v-for="item in historyStore.getHistory"
        :key="item.historyId || item.id"
      >
        <van-cell :border="false" @click="goToNewsDetail(item.id)">
          <template #title>
            <div class="news-item">
              <div class="news-image">
                <img
                  :src="normalizeImageUrl(item.image, item.categoryId)"
                  :alt="item.title"
                  :data-category-id="item.categoryId"
                  @error="applyImageFallback"
                >
              </div>
              <div class="news-info">
                <div class="news-title">{{ item.title }}</div>
                <div class="news-meta">
                  <span>{{ item.author }}</span>
                  <span>{{ formatTime(item.publishTime) }}</span>
                  <span>浏览时间: {{ formatTime(item.viewTime) }}</span>
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
          @click.stop="confirmDelete(item)"
        />
      </div>
    </div>

    <van-empty v-else description="暂无浏览历史" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog } from 'vant'
import { useHistoryStore } from '../store/modules/history'
import { formatTime } from '../utils/formatTime'
import { applyImageFallback, normalizeImageUrl } from '../utils/imageFallback'

const router = useRouter()
const historyStore = useHistoryStore()

const onClickLeft = () => {
  router.back()
}

const goToNewsDetail = (id) => {
  router.push(`/news/detail/${id}`)
}

const removeHistory = async (item) => {
  const result = await historyStore.removeHistoryApi(item)

  if (!result.success && !result.isLocal) {
    showDialog({
      title: '提示',
      message: result.message || '删除失败，请稍后重试'
    })
  }
}

const confirmDelete = (item) => {
  showDialog({
    title: '提示',
    message: '确定要删除这条浏览记录吗？',
    showCancelButton: true
  }).then((action) => {
    if (action === 'confirm') {
      removeHistory(item)
    }
  })
}

const onClickClear = async () => {
  showDialog({
    title: '提示',
    message: '确定要清空所有浏览历史吗？',
    showCancelButton: true
  }).then(async (action) => {
    if (action !== 'confirm') {
      return
    }

    const result = await historyStore.clearHistoryApi()
    if (!result.success && !result.isLocal) {
      showDialog({
        title: '提示',
        message: result.message || '清空失败，请稍后重试'
      })
    }
  })
}

onMounted(() => {
  historyStore.getHistoryListApi()
})
</script>

<style scoped>
.history-container {
  padding-top: 46px;
  padding-bottom: 20px;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.history-list {
  padding: 10px;
}

.history-item {
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
