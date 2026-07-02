'use client'

import React, { createContext, useContext, useState, useCallback } from 'react'
import type { SideFilters } from '@lib/types'

interface FilterCtx {
  filters: SideFilters
  setFilter(key: 'entidad' | 'prioridad', value: string): void
}

const Ctx = createContext<FilterCtx | null>(null)

export function FilterProvider({ children }: { children: React.ReactNode }) {
  const [filters, setFilters] = useState<SideFilters>({ entidad: '', prioridad: '' })

  const setFilter = useCallback((key: 'entidad' | 'prioridad', value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }, [])

  return <Ctx.Provider value={{ filters, setFilter }}>{children}</Ctx.Provider>
}

export function useFilters(): FilterCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useFilters must be inside FilterProvider')
  return ctx
}
