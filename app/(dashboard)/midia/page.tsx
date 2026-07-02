'use client'

import React from 'react'
import { useTasks } from '@lib/context/TaskContext'
import { MiDia } from '@/adapters/in/ui/MiDia'

export default function MiDiaPage() {
  const { tareas, usuarios, reload } = useTasks()
  return <MiDia tareas={tareas} usuarios={usuarios} onReload={reload} />
}
