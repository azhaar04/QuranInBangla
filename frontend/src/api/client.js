import axios from 'axios'

const ACCESS_TOKEN_KEY = 'qib_access_token'
const REFRESH_TOKEN_KEY = 'qib_refresh_token'
const USERNAME_KEY = 'qib_username'

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  getUsername: () => localStorage.getItem(USERNAME_KEY),
  set: (access, refresh, username) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
    if (username) localStorage.setItem(USERNAME_KEY, username)
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USERNAME_KEY)
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

// AuthContext listens for this to force isAuthenticated=false (and the
// resulting redirect to /login) — this module sits outside the React tree,
// so a DOM event is how it signals "the session is really over" upward.
function notifyLoggedOut() {
  window.dispatchEvent(new Event('auth:logout'))
}

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
      notifyLoggedOut()
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
      // ROTATE_REFRESH_TOKENS=True blacklists the refresh token used above
      // and issues a new one in `data.refresh` — must be persisted, or the
      // *next* refresh (e.g. the next day) fails with an already-blacklisted
      // token and silently strands the user on a logged-in-looking page.
      tokenStorage.set(data.access, data.refresh)
      config.headers.Authorization = `Bearer ${data.access}`
      return apiClient(config)
    } catch (refreshError) {
      tokenStorage.clear()
      notifyLoggedOut()
      throw refreshError
    }
  },
)

export default apiClient
