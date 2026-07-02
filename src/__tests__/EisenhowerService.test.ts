import { describe, it, expect } from 'vitest'
import { EisenhowerService } from '../services/EisenhowerService'
import type { TareaRaw } from '@lib/types'

function makeRaw(overrides: Partial<TareaRaw>): TareaRaw {
  return {
    id: 1, entidad: 'Xertify', proyecto: null, cliente: null,
    descripcion: 'Test', prioridad: 'Media', estado: 'No Iniciado',
    responsable: null, comentarios: null, fecha_inicio: null, fecha_fin: null,
    fecha_completado: null, lead_time_days: null, eisenhower: null,
    risk_score: null, created_by: null, created_at: '', updated_at: '',
    ...overrides,
  }
}

describe('EisenhowerService.clasificar()', () => {
  it('Urgente + Desarrollo → Q1 (Hacer ya)', () => {
    const t = makeRaw({ prioridad: 'Urgente', proyecto: 'Desarrollo' })
    expect(EisenhowerService.clasificar(t)).toBe('Q1')
  })

  it('Alta + Operaciones → Q2 (Planificar)', () => {
    const t = makeRaw({ prioridad: 'Alta', proyecto: 'Operaciones' })
    expect(EisenhowerService.clasificar(t)).toBe('Q2')
  })

  it('Urgente + Marketing → Q3 (Delegar)', () => {
    const t = makeRaw({ prioridad: 'Urgente', proyecto: 'Marketing' })
    expect(EisenhowerService.clasificar(t)).toBe('Q3')
  })

  it('Baja + Soporte → Q4 (Posponer)', () => {
    const t = makeRaw({ prioridad: 'Baja', proyecto: 'Soporte' })
    expect(EisenhowerService.clasificar(t)).toBe('Q4')
  })

  it('usa eisenhower de la API si está presente', () => {
    const t = makeRaw({ eisenhower: 'Q2' })
    expect(EisenhowerService.clasificar(t)).toBe('Q2')
  })

  it('agruparEnCuadrantes() excluye Completadas', () => {
    const svc = new EisenhowerService()
    const tareas: TareaRaw[] = [
      makeRaw({ id: 1, estado: 'En Proceso',  prioridad: 'Urgente', proyecto: 'Desarrollo' }),
      makeRaw({ id: 2, estado: 'Completado',  prioridad: 'Urgente', proyecto: 'Desarrollo' }),
    ]
    const quads = svc.agruparEnCuadrantes(tareas)
    expect(quads.Q1).toHaveLength(1)
  })
})
