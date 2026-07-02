'use client'

import React from 'react'
import { useTasks } from '@lib/context/TaskContext'
import { useFilters } from '@lib/context/FilterContext'
import { KanbanBoard } from '@/adapters/in/ui/KanbanBoard'

export default function KanbanPage() {
  const { tareas, usuarios, reload } = useTasks()
  const { filters } = useFilters()
  return (
    <KanbanBoard
      tareas={tareas}
      usuarios={usuarios}
      sideFilters={filters}
      onReload={reload}
    />
  )
}
