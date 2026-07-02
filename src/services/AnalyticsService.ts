import type { TareaRaw, Prioridad } from '@lib/types'

export const PRIO_COLORS: Record<Prioridad, string> = {
  Urgente: '#EF4444',
  Alta:    '#F59E0B',
  Media:   '#14B8A6',
  Baja:    '#64748B',
}

export interface PersonaStats {
  nombre: string
  total: number
  completadas: number
  leadTimes: number[]
  avgLeadTime: number | null
  color?: string
}

export class AnalyticsService {
  porResponsable(tareas: TareaRaw[]): PersonaStats[] {
    const map = new Map<string, PersonaStats>()

    for (const t of tareas) {
      const r = t.responsable ?? 'Sin asignar'
      if (!map.has(r)) map.set(r, { nombre: r, total: 0, completadas: 0, leadTimes: [], avgLeadTime: null })
      const s = map.get(r)!
      s.total++
      if (t.estado === 'Completado') {
        s.completadas++
        if (t.lead_time_days != null) s.leadTimes.push(t.lead_time_days)
      }
    }

    return Array.from(map.values()).map(s => ({
      ...s,
      avgLeadTime: s.leadTimes.length
        ? s.leadTimes.reduce((a, b) => a + b, 0) / s.leadTimes.length
        : null,
    })).sort((a, b) => b.total - a.total)
  }

  porPrioridad(tareas: TareaRaw[]): Record<Prioridad, number> {
    return tareas.reduce((acc, t) => {
      acc[t.prioridad] = (acc[t.prioridad] ?? 0) + 1
      return acc
    }, {} as Record<Prioridad, number>)
  }

  throughputMensual(tareas: TareaRaw[]): Array<{ mes: string; count: number }> {
    const monthly: Record<string, number> = {}
    for (const t of tareas) {
      if (t.fecha_completado) {
        const m = t.fecha_completado.slice(0, 7)
        monthly[m] = (monthly[m] ?? 0) + 1
      }
    }
    return Object.entries(monthly)
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-6)
      .map(([mes, count]) => ({ mes, count }))
  }
}
