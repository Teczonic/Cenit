import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'entidad' | 'cliente' | 'q1' | 'q2' | 'q3' | 'q4' | 'default'
  className?: string
}

const STYLES: Record<string, React.CSSProperties> = {
  entidad:  { background: 'rgba(59,130,246,.15)',   color: '#60A5FA' },
  cliente:  { background: 'rgba(20,184,166,.12)',   color: '#14B8A6' },
  q1:       { background: 'rgba(239,68,68,.15)',    color: '#FCA5A5' },
  q2:       { background: 'rgba(59,130,246,.15)',   color: '#60A5FA' },
  q3:       { background: 'rgba(245,158,11,.15)',   color: '#FCD34D' },
  q4:       { background: 'rgba(100,116,139,.15)',  color: '#64748B' },
  default:  { background: 'rgba(255,255,255,.07)',  color: '#94A3B8' },
}

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span
      className={className}
      style={{
        fontSize: 10,
        fontWeight: 500,
        padding: '2px 7px',
        borderRadius: 20,
        letterSpacing: '.3px',
        display: 'inline-block',
        ...STYLES[variant],
      }}
    >
      {children}
    </span>
  )
}
