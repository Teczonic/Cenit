import type { TareaRaw } from '@lib/types'

export interface ITareaRepository {
  getAll(): Promise<TareaRaw[]>
  create(data: Omit<TareaRaw, 'id' | 'created_at' | 'updated_at'>): Promise<TareaRaw>
  update(id: number, data: Partial<TareaRaw>): Promise<TareaRaw>
  delete(id: number): Promise<void>
  patchEstado(id: number, estado: string): Promise<TareaRaw>
}
