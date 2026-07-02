import type { TareaRaw, Cuadrante } from '@lib/types'

const PROYECTOS_IMPORTANTES = new Set([
  'Desarrollo', 'Operaciones', 'Generador', 'Wallet',
])

export const EIS_LABELS: Record<Cuadrante, string> = {
  Q1: '🔴 Q1 — Hacer ya',
  Q2: '🔵 Q2 — Planificar',
  Q3: '🟡 Q3 — Delegar',
  Q4: '⚫ Q4 — Posponer',
}

export const EIS_BADGE_CLASS: Record<Cuadrante, string> = {
  Q1: 'badge-q1',
  Q2: 'badge-q2',
  Q3: 'badge-q3',
  Q4: 'badge-q4',
}

export class EisenhowerService {
  static clasificar(tarea: TareaRaw): Cuadrante {
    if (tarea.eisenhower) return tarea.eisenhower as Cuadrante

    const esUrgente    = tarea.prioridad === 'Urgente'
    const esImportante = PROYECTOS_IMPORTANTES.has(tarea.proyecto ?? '')

    if (esUrgente && esImportante)   return 'Q1'
    if (!esUrgente && esImportante)  return 'Q2'
    if (esUrgente && !esImportante)  return 'Q3'
    return 'Q4'
  }

  agruparEnCuadrantes(tareas: TareaRaw[]): Record<Cuadrante, TareaRaw[]> {
    const quads: Record<Cuadrante, TareaRaw[]> = { Q1: [], Q2: [], Q3: [], Q4: [] }
    for (const t of tareas.filter(t => t.estado !== 'Completado')) {
      quads[EisenhowerService.clasificar(t)].push(t)
    }
    return quads
  }
}
