import type { TareaRaw, SideFilters } from '@lib/types'

export class FiltroService {
  filtrar(
    tareas: TareaRaw[],
    sideFilters: SideFilters,
    responsable: string,
    search: string,
  ): TareaRaw[] {
    const q = search.toLowerCase().trim()
    return tareas.filter(t => {
      if (sideFilters.entidad   && t.entidad    !== sideFilters.entidad)   return false
      if (sideFilters.prioridad && t.prioridad  !== sideFilters.prioridad) return false
      if (responsable           && t.responsable !== responsable)           return false
      if (q && !t.descripcion?.toLowerCase().includes(q) && !t.cliente?.toLowerCase().includes(q)) return false
      return true
    })
  }

  filtrarPorEntidad(tareas: TareaRaw[], entidad: string): TareaRaw[] {
    if (!entidad) return tareas
    return tareas.filter(t => t.entidad === entidad)
  }
}
