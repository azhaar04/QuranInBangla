import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { login as loginRequest, logout as logoutRequest } from '../api/auth'
import { tokenStorage } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => Boolean(tokenStorage.getAccess()))

  const login = useCallback(async (username, password) => {
    const { access, refresh } = await loginRequest(username, password)
    tokenStorage.set(access, refresh)
    setIsAuthenticated(true)
  }, [])

  const logout = useCallback(async () => {
    const refresh = tokenStorage.getRefresh()
    try {
      if (refresh) await logoutRequest(refresh)
    } finally {
      tokenStorage.clear()
      setIsAuthenticated(false)
    }
  }, [])

  const value = useMemo(() => ({ isAuthenticated, login, logout }), [isAuthenticated, login, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
