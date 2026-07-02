'use client'

import React from 'react'
import { useTasks } from '@lib/context/TaskContext'
import { RiskMatrix } from '@/adapters/in/ui/RiskMatrix'

export default function RiesgosPage() {
  const { tareas } = useTasks()
  return <RiskMatrix tareas={tareas} />
}
