import { describe, it, expect } from 'vitest'
import { KanbanService } from '../services/KanbanService'
import type { TareaRaw } from '@lib/types'

function makeRaw(overrides: Partial<TareaRaw>): TareaRaw {
  return {
    id: 1, entidad: 'Xertify', proyecto: 'Desarrollo', cliente: null,
    descripcion: 'Test', prioridad: 'Media', estado: 'No Iniciado',
    responsable: null, comentarios: null, fecha_inicio: null, fecha_fin: null,
    fecha_completado: null, lead_time_days: null, eisenhower: null,
    risk_score: null, created_by: null, created_at: '', updated_at: '',
    ...overrides,
  }
}

describe('KanbanService', () => {
  const svc = new KanbanService()

  it('agruparPorEstado() crea 4 columnas', () => {
    const cols = svc.agruparPorEstado([])
    expect(Object.keys(cols)).toHaveLength(4)
  })

  it('asigna tareas a la columna correcta', () => {
    const tareas: TareaRaw[] = [
      makeRaw({ id: 1, estado: 'En Proceso' }),
      makeRaw({ id: 2, estado: 'En Proceso' }),
      makeRaw({ id: 3, estado: 'Completado' }),
    ]
    const cols = svc.agruparPorEstado(tareas)
    expect(cols['En Proceso']).toHaveLength(2)
    expect(cols['Completado']).toHaveLength(1)
    expect(cols['No Iniciado']).toHaveLength(0)
  })

  it('mover tarea No Iniciado → En Proceso cambia columna', () => {
    const tareas: TareaRaw[] = [makeRaw({ id: 1, estado: 'No Iniciado' })]
    const before = svc.agruparPorEstado(tareas)
    expect(before['No Iniciado']).toHaveLength(1)

    tareas[0].estado = 'En Proceso'
    const after = svc.agruparPorEstado(tareas)
    expect(after['No Iniciado']).toHaveLength(0)
    expect(after['En Proceso']).toHaveLength(1)
  })
})
