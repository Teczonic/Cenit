import type { ITareaRepository } from '../../domain/ports/ITareaRepository'
import type { TareaRaw } from '@lib/types'
import { apiFetch } from '@lib/api'

export class TareaRepositoryImpl implements ITareaRepository {
  constructor(private readonly token: string) {}

  getAll(): Promise<TareaRaw[]> {
    return apiFetch<TareaRaw[]>('GET', '/api/tasks', undefined, this.token)
  }

  create(data: Omit<TareaRaw, 'id' | 'created_at' | 'updated_at'>): Promise<TareaRaw> {
    return apiFetch<TareaRaw>('POST', '/api/tasks', data, this.token)
  }

  update(id: number, data: Partial<TareaRaw>): Promise<TareaRaw> {
    return apiFetch<TareaRaw>('PUT', `/api/tasks/${id}`, data, this.token)
  }

  async delete(id: number): Promise<void> {
    await apiFetch<unknown>('DELETE', `/api/tasks/${id}`, undefined, this.token)
  }

  patchEstado(id: number, estado: string): Promise<TareaRaw> {
    return apiFetch<TareaRaw>('PATCH', `/api/tasks/${id}/status`, { estado }, this.token)
  }
}
