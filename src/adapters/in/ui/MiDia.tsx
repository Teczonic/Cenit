'use client'

import React, { useMemo, useState } from 'react'
import type { TareaRaw, UserRaw, Estado } from '@lib/types'
import { TaskCard } from '@components/tasks/TaskCard'
import { TaskModal } from '@components/tasks/TaskModal'
import { useToast } from '@components/ui/Toast'
import { useAuth } from '@lib/context/AuthContext'
import { TareaRepositoryImpl } from '@/adapters/out/TareaRepositoryImpl'
import { MoverTarea } from '@/domain/usecases/MoverTarea'

interface Props {
  tareas: TareaRaw[]
  usuarios: UserRaw[]
  onReload(): Promise<void>
}

interface Seccion {
  key: string
  titulo: string
  icono: string
  color: string
  vacio: string
  tareas: TareaRaw[]
}

const DAY_MS = 86400000

function diffDias(fecha: string): number {
  const hoy = new Date(); hoy.setHours(0, 0, 0, 0)
  const f = new Date(fecha); f.setHours(0, 0, 0, 0)
  return Math.round((f.getTime() - hoy.getTime()) / DAY_MS)
}

function esHoy(fecha: string | null): boolean {
  if (!fecha) return false
  return new Date(fecha).toDateString() === new Date().toDateString()
}

function saludo(): string {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días'
  if (h < 19) return 'Buenas tardes'
  return 'Buenas noches'
}

export function MiDia({ tareas, usuarios, onReload }: Props) {
  const { user, token } = useAuth()
  const { toast } = useToast()
  const [modalTask, setModalTask] = useState<TareaRaw | null>(null)

  const repo    = useMemo(() => new TareaRepositoryImpl(token), [token])
  const moverUC = useMemo(() => new MoverTarea(repo), [repo])

  const mias = useMemo(
    () => tareas.filter(t => t.responsable === user?.name),
    [tareas, user],
  )

  const secciones: Seccion[] = useMemo(() => {
    const pendientes = mias.filter(t => t.estado !== 'Completado')
    const usadas = new Set<number>()
    const tomar = (pred: (t: TareaRaw) => boolean) => {
      const r = pendientes.filter(t => !usadas.has(t.id) && pred(t))
      r.forEach(t => usadas.add(t.id))
      return r
    }
    return [
      {
        key: 'vencidas', titulo: 'Vencidas', icono: '🔴', color: 'var(--red)',
        vacio: 'Nada vencido. Bien ahí.',
        tareas: tomar(t => !!t.fecha_fin && diffDias(t.fecha_fin) < 0),
      },
      {
        key: 'hoy', titulo: 'Para hoy', icono: '📅', color: 'var(--amber)',
        vacio: 'Sin entregas para hoy.',
        tareas: tomar(t => !!t.fecha_fin && diffDias(t.fecha_fin) === 0),
      },
      {
        key: 'proximas', titulo: 'Próximas (3 días)', icono: '⚡', color: 'var(--accent2)',
        vacio: 'Nada vence en los próximos 3 días.',
        tareas: tomar(t => !!t.fecha_fin && diffDias(t.fecha_fin) <= 3),
      },
      {
        key: 'curso', titulo: 'En curso / urgentes', icono: '🎯', color: 'var(--teal)',
        vacio: 'Sin tareas en proceso.',
        tareas: tomar(t => t.estado === 'En Proceso' || t.prioridad === 'Urgente'),
      },
    ]
  }, [mias])

  const completadasHoy = mias.filter(t => esHoy(t.fecha_completado)).length
  const pendientesTotal = mias.filter(t => t.estado !== 'Completado').length
  const fechaLabel = new Date().toLocaleDateString('es', { weekday: 'long', day: 'numeric', month: 'long' })

  async function handleSave(data: Partial<TareaRaw>) {
    if (!modalTask) return
    if (!data.descripcion?.trim()) { toast('La descripción es obligatoria', 'error'); return }
    try {
      await repo.update(modalTask.id, data)
      toast('Tarea actualizada', 'success')
      setModalTask(null)
      await onReload()
    } catch (e: unknown) { toast((e as Error).message, 'error') }
  }

  async function handleQuickStatus(estado: Estado) {
    if (!modalTask) return
    try {
      await moverUC.execute(modalTask.id, estado)
      toast(`Estado: ${estado}`, 'success')
      await onReload()
    } catch (e: unknown) { toast((e as Error).message, 'error') }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, flex: 1, minHeight: 0 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, flexShrink: 0 }}>
        <span style={{ fontSize: 18, fontWeight: 500 }}>{saludo()}, {user?.name ?? ''}</span>
        <span style={{ fontSize: 13, color: 'var(--text3)', textTransform: 'capitalize' }}>{fechaLabel}</span>
        <div style={{ flex: 1 }} />
        <span style={{ fontSize: 13, color: 'var(--text2)' }}>
          <span style={{ fontFamily: 'DM Mono, monospace', color: 'var(--text)' }}>{pendientesTotal}</span> pendientes
          {' · '}
          <span style={{ fontFamily: 'DM Mono, monospace', color: 'var(--green)' }}>{completadasHoy}</span> completadas hoy
        </span>
      </div>

      {/* Secciones */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 14, minHeight: 0 }}>
        {secciones.map(s => (
          <div key={s.key} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', flexShrink: 0 }}>
            <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 14 }}>{s.icono}</span>
              <span style={{ fontSize: 13, fontWeight: 500, color: s.color }}>{s.titulo}</span>
              <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 7px', borderRadius: 20, background: 'var(--card2)', color: 'var(--text2)', fontFamily: 'DM Mono, monospace', marginLeft: 'auto' }}>
                {s.tareas.length}
              </span>
            </div>
            {s.tareas.length === 0 ? (
              <div style={{ padding: '14px 16px', fontSize: 12, color: 'var(--text3)' }}>{s.vacio}</div>
            ) : (
              <div style={{ padding: 10, display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 8 }}>
                {s.tareas.map(t => (
                  <TaskCard key={t.id} tarea={t} usuarios={usuarios} onClick={() => setModalTask(t)} />
                ))}
              </div>
            )}
          </div>
        ))}

        {mias.length === 0 && (
          <div style={{ textAlign: 'center', padding: 40, color: 'var(--text3)', fontSize: 13 }}>
            No tienes tareas asignadas. 🎉
          </div>
        )}
      </div>

      {modalTask !== null && (
        <TaskModal
          tarea={modalTask}
          usuarios={usuarios}
          currentUserName={user?.name}
          isAdmin={user?.role === 'admin'}
          onClose={() => setModalTask(null)}
          onSave={handleSave}
          onQuickStatus={handleQuickStatus}
        />
      )}
    </div>
  )
}
