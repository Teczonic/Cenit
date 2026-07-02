'use client'

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import type { TareaRaw, UserRaw } from '@lib/types'
import { apiFetch } from '@lib/api'

interface TaskCtx {
  tareas: TareaRaw[]
  usuarios: UserRaw[]
  reload(): Promise<void>
  setToken(t: string): void
}

const Ctx = createContext<TaskCtx | null>(null)

export function TaskProvider({ children }: { children: React.ReactNode }) {
  const [tareas,   setTareas]   = useState<TareaRaw[]>([])
  const [usuarios, setUsuarios] = useState<UserRaw[]>([])
  const [tok,      setTok]      = useState('')

  const reload = useCallback(async () => {
    if (!tok) return
    const [ts, us] = await Promise.all([
      apiFetch<TareaRaw[]>('GET', '/api/tasks',   undefined, tok),
      apiFetch<UserRaw[]> ('GET', '/api/users',   undefined, tok),
    ])
    setTareas(ts)
    setUsuarios(us)
  }, [tok])

  // Auto-fetch whenever the token changes (reload is recreated with new tok)
  useEffect(() => { reload() }, [reload])

  return (
    <Ctx.Provider value={{ tareas, usuarios, reload, setToken: setTok }}>
      {children}
    </Ctx.Provider>
  )
}

export function useTasks(): TaskCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useTasks must be inside TaskProvider')
  return ctx
}

