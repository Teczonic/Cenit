import React from 'react'
import type { UserRaw } from '@lib/types'
import { Avatar } from '@components/ui/Avatar'

interface Props {
  user: UserRaw
  onLogout(): void
}

export function Topbar({ user, onLogout }: Props) {
  return (
    <header style={{
      height: 56, background: 'var(--navy2)', borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center', padding: '0 20px', gap: 16, flexShrink: 0,
    }}>
      <div style={{ fontSize: 17, fontWeight: 600, letterSpacing: '-.3px', color: 'var(--text)' }}>
        Cen<span style={{ color: 'var(--accent)' }}>it</span>
      </div>
      <div style={{ flex: 1 }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Avatar name={user.name} color={user.color} size={30} fontSize={12} />
        <span style={{ fontSize: 13, color: 'var(--text2)' }}>{user.name}</span>
        <button
          onClick={onLogout}
          style={{ fontSize: 12, color: 'var(--text3)', background: 'none', padding: '6px 10px', borderRadius: 6, transition: 'color .15s, background .15s', cursor: 'pointer' }}
        >
          Salir
        </button>
      </div>
    </header>
  )
}
