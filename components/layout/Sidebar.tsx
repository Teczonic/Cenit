'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useFilters } from '@lib/context/FilterContext'
import type { Entidad, Prioridad } from '@lib/types'

const VIEWS = [
  { href: '/midia',      icon: '☀️', label: 'Mi día'     },
  { href: '/kanban',     icon: '⬛', label: 'Kanban'     },
  { href: '/eisenhower', icon: '🎯', label: 'Eisenhower' },
  { href: '/riesgos',   icon: '⚠️',  label: 'Riesgos'    },
  { href: '/analytics', icon: '📊', label: 'Analytics'  },
  { href: '/equipo',    icon: '👥', label: 'Equipo'      },
]

const ENTIDADES: Array<{ value: Entidad | ''; label: string; color: string }> = [
  { value: '',           label: 'Todas',     color: 'var(--text3)' },
  { value: 'Xertify',   label: 'Xertify',   color: 'var(--accent)' },
  { value: 'Xertiflow', label: 'Xertiflow', color: 'var(--teal)' },
]

const PRIORIDADES: Array<{ value: Prioridad | ''; label: string; color: string }> = [
  { value: '',        label: 'Todas',   color: 'var(--text3)' },
  { value: 'Urgente', label: 'Urgente', color: 'var(--red)' },
  { value: 'Alta',    label: 'Alta',    color: 'var(--amber)' },
  { value: 'Media',   label: 'Media',   color: 'var(--teal)' },
  { value: 'Baja',    label: 'Baja',    color: 'var(--text3)' },
]

export function Sidebar() {
  const path = usePathname()
  const { filters, setFilter } = useFilters()

  return (
    <aside style={{
      width: 220, background: 'var(--navy2)', borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', padding: '16px 10px', flexShrink: 0, overflowY: 'auto',
    }}>
      <div style={{ fontSize: 10, color: 'var(--text3)', letterSpacing: 1, textTransform: 'uppercase', padding: '0 8px', marginBottom: 6 }}>Vistas</div>

      {VIEWS.map(v => {
        const active = path.startsWith(v.href)
        return (
          <Link key={v.href} href={v.href} style={{ textDecoration: 'none' }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '8px 10px', borderRadius: 'var(--radius2)',
              fontSize: 13, color: active ? 'var(--accent2)' : 'var(--text2)',
              background: active ? 'rgba(59,130,246,0.15)' : 'transparent',
              fontWeight: active ? 500 : 400, marginBottom: 2, cursor: 'pointer',
              transition: 'all .15s',
            }}>
              <span style={{ fontSize: 15, width: 20, textAlign: 'center' }}>{v.icon}</span>
              {v.label}
            </div>
          </Link>
        )
      })}

      <div style={{ fontSize: 10, color: 'var(--text3)', letterSpacing: 1, textTransform: 'uppercase', padding: '0 8px', margin: '16px 0 6px' }}>Filtrar por</div>

      <div style={{ padding: '0 2px' }}>
        <div style={{ fontSize: 11, color: 'var(--text3)', marginBottom: 4, padding: '0 8px' }}>Entidad</div>
        {ENTIDADES.map(e => (
          <div key={e.value} onClick={() => setFilter('entidad', e.value)}
            style={{
              display: 'flex', alignItems: 'center', gap: 6, padding: '6px 10px', borderRadius: 6,
              fontSize: 12, color: filters.entidad === e.value ? 'var(--text)' : 'var(--text2)',
              background: filters.entidad === e.value ? 'var(--card2)' : 'transparent',
              cursor: 'pointer', transition: 'all .15s',
            }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: e.color, flexShrink: 0 }} />
            {e.label}
          </div>
        ))}

        <div style={{ fontSize: 11, color: 'var(--text3)', marginBottom: 4, padding: '0 8px', marginTop: 10 }}>Prioridad</div>
        {PRIORIDADES.map(p => (
          <div key={p.value} onClick={() => setFilter('prioridad', p.value)}
            style={{
              display: 'flex', alignItems: 'center', gap: 6, padding: '6px 10px', borderRadius: 6,
              fontSize: 12, color: filters.prioridad === p.value ? 'var(--text)' : 'var(--text2)',
              background: filters.prioridad === p.value ? 'var(--card2)' : 'transparent',
              cursor: 'pointer', transition: 'all .15s',
            }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: p.color, flexShrink: 0 }} />
            {p.label}
          </div>
        ))}
      </div>
    </aside>
  )
}