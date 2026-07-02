'use client'

import React, { useEffect, useRef } from 'react'
import type { TareaRaw, UserRaw, Estado } from '@lib/types'

const ESTADOS: Estado[] = ['No Iniciado', 'En Proceso', 'Pausado', 'Completado']
const STATUS_COLORS: Record<Estado, string> = {
  'No Iniciado': 'rgba(100,116,139,.3)',
  'En Proceso':  'rgba(59,130,246,.3)',
  'Pausado':     'rgba(245,158,11,.3)',
  'Completado':  'rgba(16,185,129,.3)',
}
const STATUS_TEXT: Record<Estado, string> = {
  'No Iniciado': '#94A3B8', 'En Proceso': '#60A5FA', 'Pausado': '#FCD34D', 'Completado': '#6EE7B7',
}

interface Props {
  tarea: TareaRaw | null
  usuarios: UserRaw[]
  currentUserName?: string
  isAdmin?: boolean
  onClose(): void
  onSave(data: Partial<TareaRaw>): Promise<void>
  onDelete?(): Promise<void>
  onQuickStatus?(estado: Estado): Promise<void>
}

export function TaskModal({ tarea, usuarios, currentUserName, isAdmin, onClose, onSave, onDelete, onQuickStatus }: Props) {
  const descRef    = useRef<HTMLTextAreaElement>(null)
  const entRef     = useRef<HTMLSelectElement>(null)
  const projRef    = useRef<HTMLSelectElement>(null)
  const clientRef  = useRef<HTMLInputElement>(null)
  const respRef    = useRef<HTMLSelectElement>(null)
  const prioRef    = useRef<HTMLSelectElement>(null)
  const estadoRef  = useRef<HTMLSelectElement>(null)
  const comentRef  = useRef<HTMLTextAreaElement>(null)
  const inicioRef  = useRef<HTMLInputElement>(null)
  const finRef     = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (tarea) {
      if (descRef.current)   descRef.current.value   = tarea.descripcion ?? ''
      if (entRef.current)    entRef.current.value    = tarea.entidad ?? 'Xertify'
      if (projRef.current)   projRef.current.value   = tarea.proyecto ?? ''
      if (clientRef.current) clientRef.current.value = tarea.cliente ?? ''
      if (respRef.current)   respRef.current.value   = tarea.responsable ?? ''
      if (prioRef.current)   prioRef.current.value   = tarea.prioridad ?? 'Media'
      if (estadoRef.current) estadoRef.current.value = tarea.estado ?? 'No Iniciado'
      if (comentRef.current) comentRef.current.value = tarea.comentarios ?? ''
      if (inicioRef.current) inicioRef.current.value = tarea.fecha_inicio?.slice(0, 10) ?? ''
      if (finRef.current)    finRef.current.value    = tarea.fecha_fin?.slice(0, 10) ?? ''
    } else {
      if (descRef.current)   descRef.current.value   = ''
      if (entRef.current)    entRef.current.value    = 'Xertify'
      if (projRef.current)   projRef.current.value   = ''
      if (clientRef.current) clientRef.current.value = ''
      if (respRef.current)   respRef.current.value   = currentUserName ?? ''
      if (prioRef.current)   prioRef.current.value   = 'Media'
      if (estadoRef.current) estadoRef.current.value = 'No Iniciado'
      if (comentRef.current) comentRef.current.value = ''
      if (inicioRef.current) inicioRef.current.value = new Date().toISOString().slice(0, 10)
      if (finRef.current)    finRef.current.value    = ''
    }
  }, [tarea, currentUserName])

  const collect = () => ({
    descripcion:  descRef.current?.value.trim() ?? '',
    entidad:      (entRef.current?.value ?? 'Xertify') as TareaRaw['entidad'],
    proyecto:     projRef.current?.value || null,
    cliente:      clientRef.current?.value || null,
    responsable:  respRef.current?.value || null,
    prioridad:    (prioRef.current?.value ?? 'Media') as TareaRaw['prioridad'],
    estado:       (estadoRef.current?.value ?? 'No Iniciado') as TareaRaw['estado'],
    comentarios:  comentRef.current?.value || null,
    fecha_inicio: inicioRef.current?.value || null,
    fecha_fin:    finRef.current?.value || null,
  })

  const inputStyle: React.CSSProperties = {
    background: 'var(--navy3)', border: '1px solid var(--border2)', borderRadius: 8,
    padding: '9px 12px', color: 'var(--text)', fontSize: 13, width: '100%',
  }
  const labelStyle: React.CSSProperties = { fontSize: 12, color: 'var(--text2)', marginBottom: 4, display: 'block' }

  return (
    <div
      onClick={e => { if ((e.target as HTMLElement).dataset.backdrop) onClose() }}
      data-backdrop="true"
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,.6)', zIndex: 500,
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20,
        animation: 'fadeIn .15s ease',
      }}
    >
      <div
        style={{
          background: 'var(--navy2)', border: '1px solid var(--border2)', borderRadius: 16,
          width: '100%', maxWidth: 560, maxHeight: '90vh', overflowY: 'auto',
          animation: 'slideUp .2s ease',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 20px 14px', borderBottom: '1px solid var(--border)' }}>
          <span style={{ fontSize: 16, fontWeight: 500 }}>{tarea ? 'Editar tarea' : 'Nueva tarea'}</span>
          <button onClick={onClose} style={{ width: 28, height: 28, borderRadius: 6, background: 'var(--card2)', color: 'var(--text2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16 }}>✕</button>
        </div>

        <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div>
            <label style={labelStyle}>Descripción *</label>
            <textarea ref={descRef} placeholder="¿Qué hay que hacer?" rows={3} style={{ ...inputStyle, resize: 'vertical', minHeight: 72 }} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={labelStyle}>Entidad</label>
              <select ref={entRef} style={inputStyle}>
                <option>Xertify</option><option>Xertiflow</option>
              </select>
            </div>
            <div>
              <label style={labelStyle}>Proyecto</label>
              <select ref={projRef} style={inputStyle}>
                <option value="">— seleccionar —</option>
                {['Operaciones','Desarrollo','Generador','Soporte','Marketing','Wallet','Scrapi','Comercial'].map(p => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Cliente</label>
              <input ref={clientRef} style={inputStyle} placeholder="Javeriana, Interno…" />
            </div>
            <div>
              <label style={labelStyle}>Responsable</label>
              <select ref={respRef} style={inputStyle}>
                <option value="">Sin asignar</option>
                {usuarios.map(u => <option key={u.id} value={u.name}>{u.name}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Prioridad</label>
              <select ref={prioRef} style={inputStyle}>
                <option>Urgente</option><option>Alta</option><option>Media</option><option>Baja</option>
              </select>
            </div>
            <div>
              <label style={labelStyle}>Estado</label>
              <select ref={estadoRef} style={inputStyle}>
                {ESTADOS.map(e => <option key={e}>{e}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Fecha inicio</label>
              <input ref={inicioRef} type="date" style={inputStyle} />
            </div>
            <div>
              <label style={labelStyle}>Fecha fin</label>
              <input ref={finRef} type="date" style={inputStyle} />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Comentarios</label>
              <textarea ref={comentRef} rows={2} placeholder="Notas, dependencias…" style={{ ...inputStyle, resize: 'vertical' }} />
            </div>
          </div>

          {tarea && onQuickStatus && (
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center', marginTop: 4 }}>
              <span style={{ fontSize: 11, color: 'var(--text3)' }}>Mover a:</span>
              {ESTADOS.map(e => (
                <button key={e} onClick={() => onQuickStatus(e)}
                  style={{ fontSize: 11, padding: '4px 10px', borderRadius: 20, border: `1px solid ${STATUS_COLORS[e]}`, color: STATUS_TEXT[e], background: 'var(--navy3)', cursor: 'pointer' }}>
                  {e}
                </button>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 10, padding: '14px 20px', borderTop: '1px solid var(--border)' }}>
          {tarea && isAdmin && onDelete && (
            <button onClick={onDelete} style={{ background: 'rgba(239,68,68,.15)', color: '#FCA5A5', borderRadius: 8, padding: '8px 16px', fontSize: 13, marginRight: 'auto', cursor: 'pointer' }}>
              Eliminar
            </button>
          )}
          <button onClick={onClose} style={{ background: 'var(--card2)', color: 'var(--text2)', borderRadius: 8, padding: '8px 16px', fontSize: 13, cursor: 'pointer' }}>
            Cancelar
          </button>
          <button onClick={() => onSave(collect())} style={{ background: 'var(--accent)', color: '#fff', borderRadius: 8, padding: '8px 20px', fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>
            Guardar
          </button>
        </div>
      </div>
    </div>
  )
}
