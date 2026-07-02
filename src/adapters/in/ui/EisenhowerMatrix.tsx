'use client'

import React, { useMemo } from 'react'
import type { TareaRaw, UserRaw, Cuadrante } from '@lib/types'
import { EisenhowerService, EIS_LABELS } from '@/services/EisenhowerService'

const eisSvc = new EisenhowerService()

const QUAD_COLORS: Record<Cuadrante, string> = {
  Q1: 'rgba(239,68,68,.08)',
  Q2: 'rgba(59,130,246,.08)',
  Q3: 'rgba(245,158,11,.08)',
  Q4: 'rgba(100,116,139,.08)',
}

interface Props { tareas: TareaRaw[]; usuarios: UserRaw[] }

export function EisenhowerMatrix({ tareas }: Props) {
  const quads = useMemo(() => eisSvc.agruparEnCuadrantes(tareas), [tareas])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, flex: 1 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
        <span style={{ fontSize: 16, fontWeight: 500 }}>Matriz Eisenhower</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4, fontSize: 11, color: 'var(--text3)', textAlign: 'center', marginBottom: 4 }}>
        <div>URGENTE</div><div>NO URGENTE</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, flex: 1 }}>
        {(['Q1','Q2','Q3','Q4'] as Cuadrante[]).map(q => (
          <div key={q} style={{ background: QUAD_COLORS[q], border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 14, minHeight: 200, overflowY: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 500, marginBottom: 10 }}>
              <span>{EIS_LABELS[q]}</span>
              <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 7px', borderRadius: 20, background: 'var(--card2)', color: 'var(--text2)', fontFamily: 'DM Mono, monospace', marginLeft: 'auto' }}>
                {quads[q].length}
              </span>
            </div>
            {quads[q].slice(0, 8).map(t => (
              <div key={t.id} style={{ background: 'var(--navy2)', border: '1px solid var(--border)', borderRadius: 6, padding: '7px 10px', marginBottom: 6, fontSize: 12, color: 'var(--text2)', cursor: 'pointer', transition: 'border-color .15s' }}>
                <div style={{ fontWeight: 500, color: 'var(--text)' }}>{t.descripcion.slice(0, 60)}{t.descripcion.length > 60 ? '…' : ''}</div>
                <div style={{ fontSize: 10, color: 'var(--text3)', marginTop: 3 }}>{t.responsable ?? 'Sin asignar'} · {t.entidad}</div>
              </div>
            ))}
            {quads[q].length > 8 && <div style={{ fontSize: 11, color: 'var(--text3)', padding: '4px 8px' }}>+{quads[q].length - 8} más…</div>}
          </div>
        ))}
      </div>
    </div>
  )
}
