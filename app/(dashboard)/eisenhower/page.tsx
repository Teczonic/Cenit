'use client'

import React from 'react'
import { useTasks } from '@lib/context/TaskContext'
import { EisenhowerMatrix } from '@/adapters/in/ui/EisenhowerMatrix'

export default function EisenhowerPage() {
  const { tareas, usuarios } = useTasks()
  return <EisenhowerMatrix tareas={tareas} usuarios={usuarios} />
}
