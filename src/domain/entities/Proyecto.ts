import type { Tarea, Prioridad, Estado } from './Tarea'

export interface Metricas {
  total: number
  completadas: number
  enProceso: number
  vencidas: number
  tasaCompletado: number
}

export class Proyecto {
  constructor(
    readonly nombre: string,
    readonly entidad: string,
    private tareas: Tarea[],
  ) {}

  agregarTarea(tarea: Tarea): void {
    this.tareas.push(tarea)
  }

  obtenerMetricas(): Metricas {
    const hoy = new Date()
    const total       = this.tareas.length
    const completadas = this.tareas.filter(t => t.estado === 'Completado').length
    const enProceso   = this.tareas.filter(t => t.estado === 'En Proceso').length
    const vencidas    = this.tareas.filter(t => t.estaVencida()).length
    return {
      total,
      completadas,
      enProceso,
      vencidas,
      tasaCompletado: total > 0 ? completadas / total : 0,
    }
  }

  filtrarPorPrioridad(prioridad: Prioridad): Tarea[] {
    return this.tareas.filter(t => t.prioridad === prioridad)
  }

  filtrarPorEstado(estado: Estado): Tarea[] {
    return this.tareas.filter(t => t.estado === estado)
  }
}
