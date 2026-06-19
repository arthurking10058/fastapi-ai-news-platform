<template>
  <div class="home">
    <van-nav-bar :title="$t('home.title')" fixed />

    <div class="more-options">
      <div class="more-tab" @click="goToCategory">
        {{ $t('home.more') }} <van-icon name="arrow" />
      </div>
    </div>

    <div class="category-tabs">
      <van-tabs v-model:active="activeTab" sticky swipeable animated>
        <van-tab
          v-for="category in displayCategories"
          :key="category.id"
          :title="getCategoryTranslation(category.name)"
        >
          <van-pull-refresh v-model="newsStore.refreshing" @refresh="onRefresh">
            <div v-if="newsStore.initialLoading" class="skeleton-list">
              <div v-for="index in 4" :key="index" class="skeleton-item">
                <div class="skeleton skeleton-image"></div>
                <div class="skeleton-content">
                  <div class="skeleton skeleton-title"></div>
                  <div class="skeleton skeleton-desc"></div>
                  <div class="skeleton skeleton-meta"></div>
                </div>
              </div>
            </div>
            <van-list
              v-else
              v-model:loading="newsStore.loading"
              :finished="newsStore.finished"
              :finished-text="$t('home.noMore')"
              @load="onLoad"
            >
              <news-item
                v-for="item in newsStore.newsList"
                :key="item.id"
                :news="item"
              />
            </van-list>
          </van-pull-refresh>
        </van-tab>
      </van-tabs>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import NewsItem from '../components/NewsItem.vue'
import TabBar from '../components/TabBar.vue'
import { useNewsStore } from '../store/modules/news'

const newsStore = useNewsStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const activeTab = ref(0)
const tabsTop = ref(0)

const displayCategories = computed(() =>
  newsStore.categories.filter(category => category.name !== '更多')
)

const getCategoryTranslation = (categoryName) => {
  const categoryMap = {
    头条: 'headline',
    社会: 'society',
    国内: 'domestic',
    国际: 'international',
    娱乐: 'entertainment',
    体育: 'sports',
    军事: 'military',
    科技: 'technology',
    财经: 'finance',
    更多: 'more'
  }

  const key = categoryMap[categoryName]
  return key ? t(`home.categories.${key}`) : categoryName
}

const goToCategory = () => {
  router.push('/category')
}

const updateTabsPosition = () => {
  const tabsElement = document.querySelector('.van-tabs__wrap')
  if (tabsElement) {
    tabsTop.value = tabsElement.getBoundingClientRect().top
  }
}

const handleScroll = () => {
  updateTabsPosition()
}

watch(
  () => route.query.categoryId,
  (newCategoryId) => {
    if (!newCategoryId || displayCategories.value.length === 0) {
      return
    }

    const categoryId = parseInt(newCategoryId, 10)
    const index = displayCategories.value.findIndex(cat => cat.id === categoryId)

    if (index !== -1) {
      activeTab.value = index
      newsStore.changeCategory(categoryId)
    }
  },
  { immediate: true }
)

watch(activeTab, (newVal) => {
  const category = displayCategories.value[newVal]
  if (!category) {
    return
  }
  newsStore.changeCategory(category.id)
})

onMounted(async () => {
  await newsStore.getCategories()

  const routeCategoryId = Number.parseInt(route.query.categoryId, 10)
  if (route.query.categoryId && Number.isInteger(routeCategoryId)) {
    const matchedCategory = displayCategories.value.find(category => category.id === routeCategoryId)
    if (matchedCategory) {
      activeTab.value = displayCategories.value.findIndex(category => category.id === routeCategoryId)
      newsStore.currentCategory = routeCategoryId
    }
  } else if (displayCategories.value.length > 0) {
    newsStore.currentCategory = displayCategories.value[0].id
  }

  await newsStore.getNewsList(true)

  const prefetchCategories = displayCategories.value
    .filter(category => category.id !== newsStore.currentCategory)
    .slice(0, 2)

  prefetchCategories.forEach((category) => {
    newsStore.prefetchFirstPage(category.id)
  })

  setTimeout(updateTabsPosition, 300)
  window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})

const onRefresh = () => {
  newsStore.getNewsList(true)
}

const onLoad = () => {
  newsStore.getNewsList()
}
</script>

<style scoped>
.home {
  padding-top: 46px;
  padding-bottom: 50px;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.category-tabs {
  margin-bottom: 10px;
  position: relative;
}

:deep(.van-tabs__wrap) {
  background-color: #fff;
}

:deep(.van-tab) {
  font-size: 14px;
}

:deep(.van-tab--active) {
  font-weight: bold;
  color: #1989fa;
}

.more-options {
  position: fixed;
  right: 0;
  background-color: #fff;
  padding: 0;
  border-radius: 4px 0 0 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  top: v-bind('tabsTop + "px"');
  height: 44px;
  display: flex;
  align-items: center;
}

.more-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #1989fa;
  font-weight: bold;
  height: 100%;
  padding: 0 10px;
}

.dropdown-menu {
  position: absolute;
  right: 15px;
  top: 40px;
  min-width: 100px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  z-index: 999;
}

.dropdown-item {
  padding: 10px 15px;
  text-align: center;
  border-bottom: 1px solid #f5f5f5;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.skeleton-list {
  padding: 8px 0;
}

.skeleton-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background-color: #fff;
  border-bottom: 1px solid #f2f2f2;
}

.skeleton-image {
  width: 110px;
  height: 80px;
  border-radius: 4px;
  flex-shrink: 0;
}

.skeleton-content {
  flex: 1;
}

.skeleton-title {
  height: 18px;
  width: 85%;
  border-radius: 6px;
  margin-bottom: 12px;
}

.skeleton-desc {
  height: 14px;
  width: 100%;
  border-radius: 6px;
  margin-bottom: 12px;
}

.skeleton-meta {
  height: 12px;
  width: 60%;
  border-radius: 6px;
}
</style>
