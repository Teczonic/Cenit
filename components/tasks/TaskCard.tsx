import React from 'react'
import type { TareaRaw, UserRaw } from '@lib/types'
import { Badge } from '@components/ui/Badge'
import { Avatar } from '@components/ui/Avatar'
import { EisenhowerService } from '@/services/EisenhowerService'

const PRIO_COLOR: Record<string, string> = {
  Urgente: '#EF4444', Alta: '#F59E0B', Media: '#14B8A6', Baja: '#64748B',
}

const EIS_VARIANT: Record<string, 'q1' | 'q2' | 'q3' | 'q4'> = {
  Q1: 'q1', Q2: 'q2', Q3: 'q3', Q4: 'q4',
}

interface Props {
  tarea: TareaRaw
  usuarios: UserRaw[]
  onClick(): void
}

function userColor(name: string, usuarios: UserRaw[]): string {
  return usuarios.find(u => u.name === name)?.color ?? '#64748B'
}

function dateLabel(fechaFin: string | null, estado: string): { text: string; color: string } | null {
  if (!fechaFin) return null
  const ff   = new Date(fechaFin)
  const diff = Math.round((ff.getTime() - Date.now()) / 86400000)
  if (diff < 0 && estado !== 'Completado') return { text: '🔴 vencida', color: 'var(--red)' }
  if (diff <= 3) return { text: `⚡ ${diff}d`, color: 'var(--amber)' }
  return { text: ff.toLocaleDateString('es', { day: '2-digit', month: 'short' }), color: 'var(--text3)' }
}

export function TaskCard({ tarea: t, usuarios, onClick }: Props) {
  const eis   = EisenhowerService.clasificar(t)
  const dl    = dateLabel(t.fecha_fin, t.estado)
  const color = userColor(t.responsable ?? '', usuarios)

  return (
    <div
      onClick={onClick}
      style={{
        background: 'var(--navy2)', border: '1px solid var(--border)', borderRadius: 'var(--radius2)',
        padding: '10px 12px', cursor: 'pointer', animation: 'fadeUp .25s ease both',
        transition: 'border-color .15s, background .15s',
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border2)'
        ;(e.currentTarget as HTMLDivElement).style.background = 'var(--navy3)'
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border)'
        ;(e.currentTarget as HTMLDivElement).style.background = 'var(--navy2)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6, marginBottom: 6 }}>
        <div style={{ width: 7, height: 7, borderRadius: '50%', background: PRIO_COLOR[t.prioridad] ?? '#64748B', flexShrink: 0, marginTop: 4 }} />
        <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.4, flex: 1 }}>{t.descripcion}</div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
        <Badge variant="entidad">{t.entidad}</Badge>
        {t.cliente && t.cliente !== 'Interno' && <Badge variant="cliente">{t.cliente}</Badge>}
        <Badge variant={EIS_VARIANT[eis]}>{eis}</Badge>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 8 }}>
        {dl && <span style={{ fontSize: 11, color: dl.color, fontFamily: 'DM Mono, monospace' }}>{dl.text}</span>}
        {t.lead_time_days != null && (
          <span style={{ fontSize: 10, fontFamily: 'DM Mono, monospace', color: 'var(--text3)', padding: '1px 5px', background: 'var(--card2)', borderRadius: 4 }}>
            {t.lead_time_days}d
          </span>
        )}
        {t.responsable && (
          <div style={{ marginLeft: 'auto' }}>
            <Avatar name={t.responsable} color={color} size={20} fontSize={8} />
          </div>
        )}
      </div>
    </div>
  )
}
