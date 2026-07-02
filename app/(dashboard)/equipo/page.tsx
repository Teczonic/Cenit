'use client'

import React from 'react'
import { useTasks } from '@lib/context/TaskContext'
import { useAuth } from '@lib/context/AuthContext'
import { Avatar } from '@components/ui/Avatar'

export default function EquipoPage() {
  const { tareas, usuarios } = useTasks()
  const { user } = useAuth()

  const stats: Record<string, { active: number; total: number }> = {}
  for (const t of tareas) {
    const r = t.responsable ?? 'Sin asignar'
    if (!stats[r]) stats[r] = { active: 0, total: 0 }
    stats[r].total++
    if (t.estado === 'En Proceso') stats[r].active++
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, flex: 1 }}>
      <div style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
        <span style={{ fontSize: 16, fontWeight: 500 }}>Equipo</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12 }}>
        {usuarios.map(u => {
          const s = stats[u.name] ?? { active: 0, total: 0 }
          const isMe = u.id === user?.id
          return (
            <div key={u.id} style={{
              background: 'var(--card)', border: `1px solid ${isMe ? 'var(--accent)' : 'var(--border)'}`,
              borderRadius: 'var(--radius)', padding: 16, display: 'flex', alignItems: 'center', gap: 12,
            }}>
              <Avatar name={u.name} color={u.color} size={42} fontSize={14} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 2 }}>{u.name}</div>
                <div style={{ fontSize: 12, color: 'var(--text3)' }}>{u.role === 'admin' ? '⭐ Admin' : 'Miembro'}</div>
                <div style={{ display: 'flex', gap: 12, marginTop: 6 }}>
                  <div style={{ fontSize: 11, color: 'var(--text2)' }}>Activas: <span style={{ fontWeight: 500, color: 'var(--text)' }}>{s.active}</span></div>
                  <div style={{ fontSize: 11, color: 'var(--text2)' }}>Total: <span style={{ fontWeight: 500, color: 'var(--text)' }}>{s.total}</span></div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
