export class RiskScore {
  constructor(
    readonly probabilidad: number,
    readonly impacto: number,
    readonly coberturaTest: number,
  ) {}

  calcular(): number {
    return this.probabilidad * this.impacto * (1 - this.coberturaTest)
  }

  nivel(): 'crítico' | 'alto' | 'medio' | 'bajo' {
    const s = this.calcular()
    if (s >= 0.5) return 'crítico'
    if (s >= 0.3) return 'alto'
    if (s >= 0.15) return 'medio'
    return 'bajo'
  }

  static fromRawScore(raw: number): RiskScore {
    const normalized = Math.min(raw / 100, 1)
    const prob = Math.sqrt(normalized)
    const imp  = Math.sqrt(normalized)
    return new RiskScore(prob, imp, 0)
  }
}
