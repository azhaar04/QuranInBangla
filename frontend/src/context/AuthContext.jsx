import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { login as loginRequest, logout as logoutRequest } from '../api/auth'
import { tokenStorage } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => Boolean(tokenStorage.getAccess()))
  const [username, setUsername] = useState(() => tokenStorage.getUsername())

  // Fired by api/client.js when a request's access token is expired AND the
  // refresh token is also invalid/expired — tokens are already cleared at
  // that point, this just makes the UI reflect it (redirects via
  // ProtectedRoute) instead of leaving the user stuck on a page that looks
  // logged-in but can't load anything.
  useEffect(() => {
    function handleForcedLogout() {
      setUsername(null)
      setIsAuthenticated(false)
    }
    window.addEventListener('auth:logout', handleForcedLogout)
    return () => window.removeEventListener('auth:logout', handleForcedLogout)
  }, [])

  const login = useCallback(async (username, password) => {
    const { access, refresh } = await loginRequest(username, password)
    tokenStorage.set(access, refresh, username)
    setUsername(username)
    setIsAuthenticated(true)
  }, [])

  const logout = useCallback(async () => {
    const refresh = tokenStorage.getRefresh()
    try {
      if (refresh) await logoutRequest(refresh)
    } finally {
      tokenStorage.clear()
      setUsername(null)
      setIsAuthenticated(false)
    }
  }, [])

  const value = useMemo(
    () => ({ isAuthenticated, username, login, logout }),
    [isAuthenticated, username, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
