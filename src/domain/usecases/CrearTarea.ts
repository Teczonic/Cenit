import type { ITareaRepository } from '../ports/ITareaRepository'
import type { TareaRaw } from '@lib/types'

export class CrearTarea {
  constructor(private readonly repo: ITareaRepository) {}

  async execute(data: Omit<TareaRaw, 'id' | 'created_at' | 'updated_at'>): Promise<TareaRaw> {
    if (!data.descripcion?.trim()) {
      throw new Error('La descripción es obligatoria')
    }
    return this.repo.create(data)
  }
}
