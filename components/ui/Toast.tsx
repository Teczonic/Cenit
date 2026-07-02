'use client'

import React, { createContext, useContext, useState, useCallback } from 'react'

interface ToastItem { id: number; msg: string; type: 'success' | 'error' }

interface ToastCtx { toast(msg: string, type?: 'success' | 'error'): void }

const Ctx = createContext<ToastCtx | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([])
  let next = 0

  const toast = useCallback((msg: string, type: 'success' | 'error' = 'success') => {
    const id = ++next
    setItems(p => [...p, { id, msg, type }])
    setTimeout(() => setItems(p => p.filter(i => i.id !== id)), 3000)
  }, [])

  return (
    <Ctx.Provider value={{ toast }}>
      {children}
      <div style={{ position: 'fixed', bottom: 20, right: 20, zIndex: 9999, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {items.map(i => (
          <div key={i.id} style={{
            background: 'var(--navy3)', border: '1px solid var(--border2)',
            borderLeft: `3px solid ${i.type === 'success' ? 'var(--green)' : 'var(--red)'}`,
            borderRadius: 10, padding: '12px 16px', fontSize: 13, color: 'var(--text)',
            animation: 'slideInRight .25s ease',
          }}>
            {i.msg}
          </div>
        ))}
      </div>
    </Ctx.Provider>
  )
}

export function useToast(): ToastCtx {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useToast must be inside ToastProvider')
  return ctx
}
