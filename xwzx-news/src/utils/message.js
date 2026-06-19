export function normalizeMessage(value, fallback = '操作失败，请稍后重试') {
  if (!value) {
    return fallback
  }

  if (typeof value === 'string') {
    return value
  }

  if (typeof value?.message === 'string') {
    return value.message
  }

  try {
    return JSON.stringify(value, ensureAsciiReplacer)
  } catch {
    return fallback
  }
}

function ensureAsciiReplacer(_key, currentValue) {
  if (currentValue instanceof Error) {
    return currentValue.message
  }
  return currentValue
}
