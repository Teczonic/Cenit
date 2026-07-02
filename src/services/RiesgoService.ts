import type { TareaRaw } from '@lib/types'

export type NivelRiesgo = 'crítico' | 'alto' | 'medio' | 'bajo'

export interface TareaConRiesgo extends TareaRaw {
  nivelRiesgo: NivelRiesgo
  scoreNormalizado: number
}

export class RiesgoService {
  static nivelDesdeScore(score: number): NivelRiesgo {
    if (score >= 15) return 'crítico'
    if (score >= 8)  return 'alto'
    if (score >= 4)  return 'medio'
    return 'bajo'
  }

  ordenarPorRiesgo(tareas: TareaRaw[]): TareaConRiesgo[] {
    return tareas
      .filter(t => t.estado !== 'Completado' && t.risk_score != null)
      .sort((a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0))
      .slice(0, 30)
      .map(t => ({
        ...t,
        nivelRiesgo:      RiesgoService.nivelDesdeScore(t.risk_score ?? 0),
        scoreNormalizado: t.risk_score ?? 0,
      }))
  }
}
