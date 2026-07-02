import { describe, it, expect } from 'vitest'
import { RiskScore } from '../domain/entities/RiskScore'

describe('RiskScore', () => {
  it('calcular(): 0.8 × 0.9 × (1-0.2) = 0.576', () => {
    const rs = new RiskScore(0.8, 0.9, 0.2)
    expect(rs.calcular()).toBeCloseTo(0.576)
  })

  it('nivel() crítico cuando score >= 0.5', () => {
    const rs = new RiskScore(0.8, 0.9, 0.2)
    expect(rs.nivel()).toBe('crítico')
  })

  it('nivel() alto cuando score >= 0.3 y < 0.5', () => {
    const rs = new RiskScore(0.7, 0.6, 0.3)
    expect(rs.calcular()).toBeCloseTo(0.294)
    expect(rs.nivel()).toBe('medio')
  })

  it('nivel() bajo cuando score < 0.15', () => {
    const rs = new RiskScore(0.1, 0.1, 0.9)
    expect(rs.nivel()).toBe('bajo')
  })

  it('calcular() = 0 cuando coberturaTest = 1', () => {
    const rs = new RiskScore(1, 1, 1)
    expect(rs.calcular()).toBe(0)
  })

  it('fromRawScore(0) → score 0', () => {
    const rs = RiskScore.fromRawScore(0)
    expect(rs.calcular()).toBe(0)
  })
})
