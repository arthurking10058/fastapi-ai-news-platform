export const formatTime = (value) => {
  if (!value) {
    return ''
  }

  if (typeof value !== 'string') {
    return value
  }

  return value.replace('T', ' ').split('.')[0]
}
