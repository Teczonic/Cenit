'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import type { UserRaw } from '@lib/types'
import { getToken, setToken, removeToken } from '@lib/auth'
import { AuthServiceImpl } from '@/adapters/out/AuthServiceImpl'

interface AuthCtx {
  user: UserRaw | null
  token: string
  login(username: string, password: string): Promise<void>
  logout(): void
  loading: boolean
}

const Ctx = createContext<AuthCtx | null>(null)

const authSvc = new AuthServiceImpl()

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser]     = useState<UserRaw | null>(null)
  const [token, setTok]     = useState<string>('')
  const [loading, setLoad]  = useState(true)

  useEffect(() => {
    const saved = getToken()
    if (!saved) { setLoad(false); return }
    authSvc.me(saved)
      .then(u  => { setUser(u); setTok(saved) })
      .catch(() => { removeToken() })
      .finally(() => setLoad(false))
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const res = await authSvc.login(username, password)
    setToken(res.token)
    setTok(res.token)
    setUser(res.user)
  }, [])

  const logout = useCallback(() => {
    authSvc.logout()
    setTok('')
    setUser(null)
  }, [])

  return <Ctx.Provider value={{ user, token, login, logout, loading }}>{children}</Ctx.Provider>
}

export function useAuth(): AuthCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
