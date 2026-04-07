import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

const TOKEN_KEY = 'medcall_token'
const USER_KEY  = 'medcall_user'

function readStorage() {
  try {
    return {
      token: localStorage.getItem(TOKEN_KEY) || null,
      user:  JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
    }
  } catch {
    return { token: null, user: null }
  }
}

export function AuthProvider({ children }) {
  const [{ token, user }, setAuth] = useState(readStorage)

  /** Called after successful login or registration. */
  const login = (tokenStr, userData) => {
    localStorage.setItem(TOKEN_KEY, tokenStr)
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
    setAuth({ token: tokenStr, user: userData })
  }

  /** Patch user fields without re-issuing a token (e.g. after saving profile). */
  const updateUser = (patch) => {
    const updated = { ...user, ...patch }
    localStorage.setItem(USER_KEY, JSON.stringify(updated))
    setAuth(prev => ({ ...prev, user: updated }))
  }

  const logout = () => {
    // Clear all auth keys synchronously before any navigation
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    // Belt-and-suspenders: wipe any legacy keys from older app versions
    localStorage.removeItem('medcall_user')
    sessionStorage.clear()
    setAuth({ token: null, user: null })
  }

  return (
    <AuthContext.Provider value={{ token, user, login, updateUser, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
