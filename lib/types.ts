export type Prioridad = 'Urgente' | 'Alta' | 'Media' | 'Baja'
export type Estado    = 'No Iniciado' | 'En Proceso' | 'Pausado' | 'Completado'
export type Entidad   = 'Xertify' | 'Xertiflow'
export type Cuadrante = 'Q1' | 'Q2' | 'Q3' | 'Q4'

export interface TareaRaw {
  id: number
  entidad: Entidad
  proyecto: string | null
  cliente: string | null
  descripcion: string
  prioridad: Prioridad
  estado: Estado
  responsable: string | null
  comentarios: string | null
  fecha_inicio: string | null
  fecha_fin: string | null
  fecha_completado: string | null
  lead_time_days: number | null
  eisenhower: Cuadrante | null
  risk_score: number | null
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface UserRaw {
  id: number
  username: string
  name: string
  role: 'admin' | 'member'
  color: string
}

export interface LoginResponse {
  token: string
  user: UserRaw
}

export interface SideFilters {
  entidad: Entidad | ''
  prioridad: Prioridad | ''
}
