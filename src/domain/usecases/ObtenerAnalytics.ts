import type { Tarea } from '../entities/Tarea'

export interface Metricas {
  totalBacklog: number
  urgentes: number
  enProceso: number
  completadas: number
  vencidas: number
  avgLeadTimeDias: number | null
  porResponsable: Record<string, { total: number; completadas: number }>
  porPrioridad: Record<string, number>
  throughputMensual: Record<string, number>
}

export class ObtenerAnalytics {
  execute(tareas: Tarea[]): Metricas {
    const hoy = new Date()
    const total       = tareas.length
    const urgentes    = tareas.filter(t => t.prioridad === 'Urgente').length
    const enProceso   = tareas.filter(t => t.estado === 'En Proceso').length
    const completadas = tareas.filter(t => t.estado === 'Completado').length
    const vencidas    = tareas.filter(t => t.estaVencida()).length

    const porResponsable: Record<string, { total: number; completadas: number }> = {}
    const porPrioridad: Record<string, number> = {}
    const throughputMensual: Record<string, number> = {}

    for (const t of tareas) {
      const r = t.responsable ?? 'Sin asignar'
      if (!porResponsable[r]) porResponsable[r] = { total: 0, completadas: 0 }
      porResponsable[r].total++
      if (t.estado === 'Completado') porResponsable[r].completadas++

      porPrioridad[t.prioridad] = (porPrioridad[t.prioridad] ?? 0) + 1
    }

    return {
      totalBacklog: total,
      urgentes,
      enProceso,
      completadas,
      vencidas,
      avgLeadTimeDias: null,
      porResponsable,
      porPrioridad,
      throughputMensual,
    }
  }
}
