import axios from 'axios'

import { apiConfig } from '../config/api'

const request = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: 10000,
})

function readStoredToken() {
  const rawUserStore = localStorage.getItem('user-store')
  if (!rawUserStore) {
    return ''
  }

  try {
    const parsed = JSON.parse(rawUserStore)
    return parsed?.token || ''
  } catch {
    return ''
  }
}

request.interceptors.request.use((config) => {
  const token = readStoredToken()
  if (!token) {
    return config
  }

  config.headers = config.headers || {}
  const authValue = token.startsWith('Bearer ') ? token : `Bearer ${token}`
  config.headers.Authorization = config.headers.Authorization || authValue
  return config
})

export function getErrorMessage(error, fallback = '网络请求失败') {
  return (
    error?.response?.data?.message ||
    error?.response?.data?.detail ||
    error?.message ||
    fallback
  )
}

export default request
