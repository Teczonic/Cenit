'use client'

import React from 'react'
import { useTasks } from '@lib/context/TaskContext'
import { AnalyticsDashboard } from '@/adapters/in/ui/AnalyticsDashboard'

export default function AnalyticsPage() {
  const { tareas, usuarios } = useTasks()
  return <AnalyticsDashboard tareas={tareas} usuarios={usuarios} />
}
