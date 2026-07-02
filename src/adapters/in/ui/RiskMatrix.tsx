'use client'

import React, { useMemo } from 'react'
import type { TareaRaw } from '@lib/types'
import { RiesgoService, type NivelRiesgo } from '@/services/RiesgoService'

const riesgoSvc = new RiesgoService()

const NIVEL_CSS: Record<NivelRiesgo, { bg: string; color: string; label: string }> = {
  crítico: { bg: 'rgba(239,68,68,.2)',   color: '#FCA5A5', label: 'CRÍTICO' },
  alto:    { bg: 'rgba(249,115,22,.2)',  color: '#FDBA74', label: 'ALTO'    },
  medio:   { bg: 'rgba(245,158,11,.2)', color: '#FCD34D', label: 'MEDIO'   },
  bajo:    { bg: 'rgba(16,185,129,.2)',  color: '#6EE7B7', label: 'BAJO'    },
}

interface Props { tareas: TareaRaw[] }

export function RiskMatrix({ tareas }: Props) {
  const sorted = useMemo(() => riesgoSvc.ordenarPorRiesgo(tareas), [tareas])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, flex: 1 }}>
      <div style={{ display: 'flex', alignItems: 'center', flexShrink: 0, gap: 10 }}>
        <span style={{ fontSize: 16, fontWeight: 500 }}>Matriz de riesgos</span>
      </div>
      <div style={{ fontSize: 12, color: 'var(--text3)' }}>
        Risk Score = Probabilidad × Impacto × (1 − Cobertura test). Mayor score → mayor atención QA.
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {sorted.length === 0 && <div style={{ color: 'var(--text3)', fontSize: 13, padding: 20 }}>Sin riesgos activos</div>}
        {sorted.map(t => {
          const css = NIVEL_CSS[t.nivelRiesgo]
          return (
            <div key={t.id} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 12px', background: 'var(--navy2)', border: '1px solid var(--border)', borderRadius: 8, cursor: 'pointer' }}>
              <span style={{ fontSize: 10, fontWeight: 600, padding: '2px 8px', borderRadius: 20, background: css.bg, color: css.color, flexShrink: 0, width: 64, textAlign: 'center' }}>
                {css.label}
              </span>
              <span style={{ fontSize: 12, color: 'var(--text)', flex: 1 }}>
                {t.descripcion.slice(0, 70)}{t.descripcion.length > 70 ? '…' : ''}
              </span>
              <span style={{ fontSize: 11, color: 'var(--text2)', flexShrink: 0 }}>{t.responsable ?? '—'}</span>
              <span style={{ fontSize: 12, fontFamily: 'DM Mono, monospace', color: 'var(--text3)', flexShrink: 0 }}>{t.risk_score}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
