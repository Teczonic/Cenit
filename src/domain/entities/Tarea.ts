import { RiskScore } from './RiskScore'
import type { Usuario } from './Usuario'

export type Prioridad = 'Urgente' | 'Alta' | 'Media' | 'Baja'
export type Estado    = 'No Iniciado' | 'En Proceso' | 'Pausado' | 'Completado'
export type Entidad   = 'Xertify' | 'Xertiflow'
export type Proyecto  =
  | 'Operaciones' | 'Desarrollo' | 'Generador' | 'Soporte'
  | 'Marketing'   | 'Wallet'     | 'Scrapi'    | 'Comercial'

export interface TareaProps {
  id: number
  descripcion: string
  entidad: Entidad
  proyecto: Proyecto | null
  cliente: string | null
  responsable: string | null
  prioridad: Prioridad
  estado: Estado
  fechaInicio: Date | null
  fechaFin: Date | null
  comentarios: string | null
  riskScore?: number
}

export class Tarea {
  readonly id: number
  descripcion: string
  entidad: Entidad
  proyecto: Proyecto | null
  cliente: string | null
  responsable: string | null
  prioridad: Prioridad
  estado: Estado
  fechaInicio: Date | null
  fechaFin: Date | null
  comentarios: string | null
  riskScore: number

  constructor(props: TareaProps) {
    this.id          = props.id
    this.descripcion = props.descripcion
    this.entidad     = props.entidad
    this.proyecto    = props.proyecto
    this.cliente     = props.cliente
    this.responsable = props.responsable
    this.prioridad   = props.prioridad
    this.estado      = props.estado
    this.fechaInicio = props.fechaInicio
    this.fechaFin    = props.fechaFin
    this.comentarios = props.comentarios
    this.riskScore   = props.riskScore ?? 0
  }

  moverEstado(nuevoEstado: Estado): void {
    this.estado = nuevoEstado
  }

  calcularRiesgo(): RiskScore {
    return RiskScore.fromRawScore(this.riskScore)
  }

  estaVencida(): boolean {
    if (!this.fechaFin || this.estado === 'Completado') return false
    return this.fechaFin < new Date()
  }

  asignarResponsable(usuario: Usuario): void {
    this.responsable = usuario.nombre
  }
}
