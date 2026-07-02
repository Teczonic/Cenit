'use client'

import React, { useMemo } from 'react'
import type { TareaRaw, UserRaw, Prioridad } from '@lib/types'
import { AnalyticsService, PRIO_COLORS } from '@/services/AnalyticsService'

const anaSvc = new AnalyticsService()

function userColor(name: string, usuarios: UserRaw[]): string {
  return usuarios.find(u => u.name === name)?.color ?? '#64748B'
}

function BarRow({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
      <span style={{ fontSize: 12, color: 'var(--text2)', width: 100, flexShrink: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{label}</span>
      <div style={{ flex: 1, height: 6, background: 'var(--navy3)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ width: `${(value / Math.max(max, 1)) * 100}%`, height: '100%', borderRadius: 3, background: color, transition: 'width .6s ease' }} />
      </div>
      <span style={{ fontSize: 11, color: 'var(--text3)', width: 30, textAlign: 'right', fontFamily: 'DM Mono, monospace' }}>{value}</span>
    </div>
  )
}

interface Props { tareas: TareaRaw[]; usuarios: UserRaw[] }

export function AnalyticsDashboard({ tareas, usuarios }: Props) {
  const byResp  = useMemo(() => anaSvc.porResponsable(tareas), [tareas])
  const byPrio  = useMemo(() => anaSvc.porPrioridad(tareas),   [tareas])
  const monthly = useMemo(() => anaSvc.throughputMensual(tareas), [tareas])

  const maxPers  = Math.max(...byResp.map(r => r.total), 1)
  const maxPrio  = Math.max(...Object.values(byPrio), 1)
  const maxMonth = Math.max(...monthly.map(m => m.count), 1)

  const card = (title: string, children: React.ReactNode) => (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 16 }}>
      <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text2)', marginBottom: 14 }}>{title}</div>
      {children}
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, flex: 1 }}>
      <div style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
        <span style={{ fontSize: 16, fontWeight: 500 }}>Analytics del equipo</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {card('Tareas por persona',
          byResp.slice(0, 8).map(r => (
            <BarRow key={r.nombre} label={r.nombre} value={r.total} max={maxPers} color={userColor(r.nombre, usuarios)} />
          ))
        )}

        {card('Distribución por prioridad',
          (Object.entries(byPrio) as [Prioridad, number][]).map(([p, v]) => (
            <BarRow key={p} label={p} value={v} max={maxPrio} color={PRIO_COLORS[p]} />
          ))
        )}

        {card('Throughput mensual (completadas)',
          <div>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 80, marginBottom: 6 }}>
              {monthly.map(m => (
                <div key={m.mes} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <span style={{ fontSize: 10, fontFamily: 'DM Mono, monospace', color: 'var(--text2)' }}>{m.count}</span>
                  <div style={{ width: '100%', borderRadius: '3px 3px 0 0', background: 'var(--accent)', height: (m.count / maxMonth) * 60 + 4, minHeight: 2 }} />
                  <span style={{ fontSize: 10, color: 'var(--text3)', whiteSpace: 'nowrap' }}>{m.mes.slice(5)}</span>
                </div>
              ))}
            </div>
            {monthly.length === 0 && <div style={{ color: 'var(--text3)', fontSize: 12 }}>Sin datos aún</div>}
          </div>
        )}

        {card('Lead time por persona (días)',
          byResp.filter(r => r.avgLeadTime != null).length === 0
            ? <div style={{ color: 'var(--text3)', fontSize: 12 }}>Sin completadas aún</div>
            : byResp
                .filter(r => r.avgLeadTime != null)
                .sort((a, b) => (a.avgLeadTime ?? 0) - (b.avgLeadTime ?? 0))
                .slice(0, 8)
                .map(r => {
                  const avg = r.avgLeadTime!
                  const fill = Math.min(avg / 10 * 100, 100)
                  const color = avg <= 2 ? '#10B981' : avg <= 5 ? '#14B8A6' : avg <= 10 ? '#F59E0B' : '#EF4444'
                  return (
                    <div key={r.nombre} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                      <span style={{ fontSize: 12, color: 'var(--text2)', width: 100, flexShrink: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.nombre}</span>
                      <div style={{ flex: 1, height: 6, background: 'var(--navy3)', borderRadius: 3, overflow: 'hidden' }}>
                        <div style={{ width: `${fill}%`, height: '100%', borderRadius: 3, background: color }} />
                      </div>
                      <span style={{ fontSize: 11, color: 'var(--text3)', width: 40, textAlign: 'right', fontFamily: 'DM Mono, monospace' }}>{avg.toFixed(1)}d</span>
                    </div>
                  )
                })
        )}
      </div>
    </div>
  )
}
