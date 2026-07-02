'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@lib/context/AuthContext'
import { useTasks } from '@lib/context/TaskContext'
import { Sidebar } from '@components/layout/Sidebar'
import { Topbar } from '@components/layout/Topbar'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, token, logout, loading } = useAuth()
  const { reload, setToken }             = useTasks()
  const router                           = useRouter()

  useEffect(() => {
    if (!loading && !user) router.replace('/login')
  }, [loading, user, router])

  useEffect(() => {
    if (token) setToken(token)
  }, [token]) // eslint-disable-line react-hooks/exhaustive-deps

  if (loading || !user) return null

  function handleLogout() { logout(); router.replace('/login') }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Topbar user={user} onLogout={handleLogout} />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar />
        <main style={{ flex: 1, overflowY: 'auto', padding: 20, display: 'flex', flexDirection: 'column', gap: 20 }}>
          {children}
        </main>
      </div>
    </div>
  )
}
