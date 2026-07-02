import type { TareaRaw, Estado } from '@lib/types'

export const ESTADOS: Estado[] = ['No Iniciado', 'En Proceso', 'Pausado', 'Completado']

export const ESTADO_COLORS: Record<Estado, string> = {
  'No Iniciado': '#64748B',
  'En Proceso':  '#3B82F6',
  'Pausado':     '#F59E0B',
  'Completado':  '#10B981',
}

export class KanbanService {
  agruparPorEstado(tareas: TareaRaw[]): Record<Estado, TareaRaw[]> {
    const cols = Object.fromEntries(ESTADOS.map(e => [e, [] as TareaRaw[]])) as Record<Estado, TareaRaw[]>
    for (const t of tareas) {
      const col = (t.estado as Estado) in cols ? (t.estado as Estado) : 'No Iniciado'
      cols[col].push(t)
    }
    return cols
  }

  colorEstado(estado: Estado): string {
    return ESTADO_COLORS[estado] ?? '#64748B'
  }
}
