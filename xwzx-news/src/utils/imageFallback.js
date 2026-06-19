import placeholderImage from '../assets/news-placeholder.svg'

const CATEGORY_FALLBACKS = {
  1: '/demo-images/headline.svg',
  2: '/demo-images/society.svg',
  3: '/demo-images/technology.svg',
  4: '/demo-images/sports.svg',
  5: '/demo-images/finance.svg',
  6: '/demo-images/society.svg',
  7: '/demo-images/technology.svg',
}

export function getCategoryFallbackImage(categoryId) {
  const fallback = CATEGORY_FALLBACKS[Number(categoryId)]
  return fallback || placeholderImage
}

export function normalizeImageUrl(image, categoryId = null) {
  if (!image || typeof image !== 'string') {
    return getCategoryFallbackImage(categoryId)
  }

  const trimmed = image.trim()
  if (!trimmed) {
    return getCategoryFallbackImage(categoryId)
  }

  if (trimmed.startsWith('/demo-images/')) {
    return trimmed
  }

  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return trimmed
  }

  return getCategoryFallbackImage(categoryId)
}

export function applyImageFallback(event) {
  const target = event?.target
  if (!target) {
    return
  }

  if (target.dataset.fallbackApplied === 'true') {
    return
  }

  target.dataset.fallbackApplied = 'true'
  target.src = getCategoryFallbackImage(target.dataset.categoryId)
}

export { placeholderImage }
