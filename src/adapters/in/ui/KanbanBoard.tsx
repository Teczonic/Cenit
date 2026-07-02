'use client'

import React, { useState, useMemo } from 'react'
import type { TareaRaw, UserRaw, SideFilters, Estado } from '@lib/types'
import { KanbanService, ESTADO_COLORS, ESTADOS } from '@/services/KanbanService'
import { FiltroService } from '@/services/FiltroService'
import { TaskCard } from '@components/tasks/TaskCard'
import { TaskModal } from '@components/tasks/TaskModal'
import { useToast } from '@components/ui/Toast'
import { useAuth } from '@lib/context/AuthContext'
import { TareaRepositoryImpl } from '@/adapters/out/TareaRepositoryImpl'
import { MoverTarea } from '@/domain/usecases/MoverTarea'

const kanban = new KanbanService()
const filtro = new FiltroService()

interface Props {
  tareas: TareaRaw[]
  usuarios: UserRaw[]
  sideFilters: SideFilters
  onReload(): Promise<void>
}

export function KanbanBoard({ tareas, usuarios, sideFilters, onReload }: Props) {
  const { user, token } = useAuth()
  const { toast } = useToast()
  const [search,    setSearch]    = useState('')
  const [respFilt,  setRespFilt]  = useState('')
  const [modalTask, setModalTask] = useState<TareaRaw | 'new' | null>(null)

  const repo     = useMemo(() => new TareaRepositoryImpl(token), [token])
  const moverUC  = useMemo(() => new MoverTarea(repo), [repo])

  const visible  = useMemo(
    () => filtro.filtrar(tareas, sideFilters, respFilt, search),
    [tareas, sideFilters, respFilt, search],
  )
  const cols = useMemo(() => kanban.agruparPorEstado(visible), [visible])

  const today = new Date()
  const urgentes  = tareas.filter(t => t.prioridad === 'Urgente').length
  const enProceso = tareas.filter(t => t.estado === 'En Proceso').length
  const completadas = tareas.filter(t => t.estado === 'Completado').length
  const vencidas  = tareas.filter(t => t.fecha_fin && new Date(t.fecha_fin) < today && t.estado !== 'Completado').length
  const lts = tareas.filter(t => t.lead_time_days != null).map(t => t.lead_time_days!)
  const avgLt = lts.length ? (lts.reduce((a, b) => a + b, 0) / lts.length).toFixed(1) : '—'

  const statCard = (label: string, value: string | number, color: string, sub: string) => (
    <div key={label} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '14px 16px' }}>
      <div style={{ fontSize: 11, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '.5px', marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 600, fontFamily: 'DM Mono, monospace', color }}>{value}</div>
      <div style={{ fontSize: 11, color: 'var(--text3)', marginTop: 4 }}>{sub}</div>
    </div>
  )

  async function handleSave(data: Partial<TareaRaw>) {
    if (!data.descripcion?.trim()) { toast('La descripción es obligatoria', 'error'); return }
    try {
      if (modalTask && modalTask !== 'new') {
        await repo.update(modalTask.id, data)
        toast('Tarea actualizada', 'success')
      } else {
        await repo.create(data as Omit<TareaRaw, 'id' | 'created_at' | 'updated_at'>)
        toast('Tarea creada', 'success')
      }
      setModalTask(null)
      await onReload()
    } catch (e: unknown) { toast((e as Error).message, 'error') }
  }

  async function handleDelete() {
    if (!modalTask || modalTask === 'new') return
    if (!confirm('¿Eliminar esta tarea?')) return
    try {
      await repo.delete(modalTask.id)
      toast('Tarea eliminada', 'success')
      setModalTask(null)
      await onReload()
    } catch (e: unknown) { toast((e as Error).message, 'error') }
  }

  async function handleQuickStatus(estado: Estado) {
    if (!modalTask || modalTask === 'new') return
    try {
      await moverUC.execute(modalTask.id, estado)
      toast(`Estado: ${estado}`, 'success')
      await onReload()
    } catch (e: unknown) { toast((e as Error).message, 'error') }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, flex: 1, minHeight: 0 }}>
      {/* Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
        <span style={{ fontSize: 16, fontWeight: 500 }}>Backlog del equipo</span>
        <div style={{ flex: 1 }} />
        <input
          value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Buscar tarea…"
          style={{ background: 'var(--navy2)', border: '1px solid var(--border2)', borderRadius: 8, padding: '7px 12px', fontSize: 13, color: 'var(--text)', width: 220 }}
        />
        <select value={respFilt} onChange={e => setRespFilt(e.target.value)}
          style={{ background: 'var(--navy2)', border: '1px solid var(--border2)', borderRadius: 8, padding: '7px 12px', fontSize: 13, color: 'var(--text2)', cursor: 'pointer' }}>
          <option value="">Todos</option>
          {usuarios.map(u => <option key={u.id} value={u.name}>{u.name}</option>)}
        </select>
        <button onClick={() => setModalTask('new')}
          style={{ background: 'var(--accent)', color: '#fff', borderRadius: 8, padding: '8px 16px', fontSize: 13, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
          + Nueva tarea
        </button>
      </div>

      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6,1fr)', gap: 10, flexShrink: 0 }}>
        {statCard('Total backlog',   tareas.length, 'var(--text)',   'tareas')}
        {statCard('Urgentes',        urgentes,       'var(--red)',    'requieren acción hoy')}
        {statCard('En proceso',      enProceso,      'var(--accent2)', 'en desarrollo')}
        {statCard('Completadas',     completadas,    'var(--green)',  'entregadas')}
        {statCard('Lead time prom',  avgLt,          'var(--teal)',   'días (completadas)')}
        {statCard('Vencidas',        vencidas,       'var(--amber)',  'fecha fin pasada')}
      </div>

      {/* Kanban board */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14, flex: 1, minHeight: 0 }}>
        {ESTADOS.map(estado => (
          <div key={estado} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: ESTADO_COLORS[estado] }} />
              <span style={{ fontSize: 13, fontWeight: 500 }}>{estado}</span>
              <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 7px', borderRadius: 20, background: 'var(--card2)', color: 'var(--text2)', fontFamily: 'DM Mono, monospace', marginLeft: 'auto' }}>
                {cols[estado].length}
              </span>
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {cols[estado].map(t => (
                <TaskCard key={t.id} tarea={t} usuarios={usuarios} onClick={() => setModalTask(t)} />
              ))}
            </div>
          </div>
        ))}
      </div>

      {modalTask !== null && (
        <TaskModal
          tarea={modalTask === 'new' ? null : modalTask}
          usuarios={usuarios}
          currentUserName={user?.name}
          isAdmin={user?.role === 'admin'}
          onClose={() => setModalTask(null)}
          onSave={handleSave}
          onDelete={handleDelete}
          onQuickStatus={handleQuickStatus}
        />
      )}
    </div>
  )
}
