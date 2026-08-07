import axios from 'axios'

const ACCESS_TOKEN_KEY = 'qib_access_token'
const REFRESH_TOKEN_KEY = 'qib_refresh_token'

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  set: (access, refresh) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshPromise = null

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    if (response?.status !== 401 || config._retried) {
      throw error
    }

    const refresh = tokenStorage.getRefresh()
    if (!refresh) {
      tokenStorage.clear()
      throw error
    }

    config._retried = true
    try {
      refreshPromise ??= axios
        .post(`${import.meta.env.VITE_API_BASE_URL}/auth/token/refresh/`, { refresh })
        .finally(() => {
          refreshPromise = null
        })
      const { data } = await refreshPromise
      tokenStorage.set(data.access)
      config.headers.Authorization = `Bearer ${data.access}`
      return apiClient(config)
    } catch (refreshError) {
      tokenStorage.clear()
      throw refreshError
    }
  },
)

export default apiClient
