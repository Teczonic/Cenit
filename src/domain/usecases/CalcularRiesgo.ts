import { RiskScore } from '../entities/RiskScore'
import type { Tarea } from '../entities/Tarea'

export class CalcularRiesgo {
  execute(tarea: Tarea): RiskScore {
    return tarea.calcularRiesgo()
  }
}
