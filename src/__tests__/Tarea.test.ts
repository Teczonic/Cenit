import { describe, it, expect } from 'vitest'
import { Tarea } from '../domain/entities/Tarea'
import type { TareaProps } from '../domain/entities/Tarea'

function makeTarea(overrides: Partial<TareaProps> = {}): Tarea {
  return new Tarea({
    id: 1,
    descripcion: 'Test task',
    entidad: 'Xertify',
    proyecto: 'Desarrollo',
    cliente: null,
    responsable: null,
    prioridad: 'Media',
    estado: 'No Iniciado',
    fechaInicio: null,
    fechaFin: null,
    comentarios: null,
    riskScore: 0,
    ...overrides,
  })
}

describe('Tarea', () => {
  it('moverEstado() actualiza el estado', () => {
    const t = makeTarea()
    t.moverEstado('En Proceso')
    expect(t.estado).toBe('En Proceso')
  })

  it('estaVencida() true cuando fechaFin pasada y no completada', () => {
    const ayer = new Date(Date.now() - 86400000)
    const t = makeTarea({ fechaFin: ayer, estado: 'En Proceso' })
    expect(t.estaVencida()).toBe(true)
  })

  it('estaVencida() false cuando estado Completado', () => {
    const ayer = new Date(Date.now() - 86400000)
    const t = makeTarea({ fechaFin: ayer, estado: 'Completado' })
    expect(t.estaVencida()).toBe(false)
  })

  it('estaVencida() false cuando sin fechaFin', () => {
    const t = makeTarea({ fechaFin: null })
    expect(t.estaVencida()).toBe(false)
  })

  it('asignarResponsable() actualiza responsable', () => {
    const t = makeTarea()
    const usuario = { id: 1, username: 'fidel', nombre: 'Fidel López', rol: 'admin', color: '#fff' } as any
    t.asignarResponsable(usuario)
    expect(t.responsable).toBe('Fidel López')
  })

  it('calcularRiesgo() retorna RiskScore válido', () => {
    const t = makeTarea({ riskScore: 50 })
    const rs = t.calcularRiesgo()
    expect(rs.calcular()).toBeGreaterThan(0)
  })
})
