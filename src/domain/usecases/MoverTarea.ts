import type { ITareaRepository } from '../ports/ITareaRepository'
import type { Estado } from '../entities/Tarea'
import type { TareaRaw } from '@lib/types'

export class MoverTarea {
  constructor(private readonly repo: ITareaRepository) {}

  async execute(tareaId: number, nuevoEstado: Estado): Promise<TareaRaw> {
    return this.repo.patchEstado(tareaId, nuevoEstado)
  }
}
