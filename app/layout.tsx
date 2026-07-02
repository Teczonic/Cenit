import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@lib/context/AuthContext'
import { TaskProvider } from '@lib/context/TaskContext'
import { FilterProvider } from '@lib/context/FilterContext'
import { ToastProvider } from '@components/ui/Toast'

export const metadata: Metadata = {
  title: 'Cenit — Team Backlog Manager',
  description: 'Gestión de backlog y productividad del equipo',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <AuthProvider>
          <TaskProvider>
            <FilterProvider>
              <ToastProvider>
                {children}
              </ToastProvider>
            </FilterProvider>
          </TaskProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
