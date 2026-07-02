import type { Tarea } from './Tarea'

export type Rol = 'admin' | 'member'

export interface IPuedeVerKanban     { verKanban(): boolean }
export interface IPuedeVerAnalytics  { verAnalytics(): boolean }
export interface IPuedeGestionarEquipo { gestionarEquipo(): boolean }
export interface IPuedeCrearTareas   { crearTareas(): boolean }
export interface IPuedeEliminarTareas { eliminarTareas(): boolean }

export type Permiso = keyof typeof PERMISOS_POR_ROL

const PERMISOS_POR_ROL = {
  verKanban:        ['admin', 'member'],
  verAnalytics:     ['admin', 'member'],
  gestionarEquipo:  ['admin'],
  crearTareas:      ['admin', 'member'],
  eliminarTareas:   ['admin'],
} as const

export class Usuario implements
  IPuedeVerKanban,
  IPuedeVerAnalytics,
  IPuedeGestionarEquipo,
  IPuedeCrearTareas,
  IPuedeEliminarTareas
{
  constructor(
    readonly id: number,
    readonly username: string,
    readonly nombre: string,
    readonly rol: Rol,
    readonly color: string,
  ) {}

  private _tareas: Tarea[] = []

  obtenerTareas(): Tarea[] {
    return this._tareas.filter(t => t.responsable === this.nombre)
  }

  cargarTareas(tareas: Tarea[]): void {
    this._tareas = tareas
  }

  obtenerPermisos(): Permiso[] {
    return (Object.keys(PERMISOS_POR_ROL) as Permiso[]).filter(p =>
      (PERMISOS_POR_ROL[p] as readonly string[]).includes(this.rol)
    )
  }

  verKanban():        boolean { return true }
  verAnalytics():     boolean { return true }
  gestionarEquipo():  boolean { return this.rol === 'admin' }
  crearTareas():      boolean { return true }
  eliminarTareas():   boolean { return this.rol === 'admin' }
}
