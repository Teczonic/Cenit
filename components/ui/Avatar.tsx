import React from 'react'
import { initials } from '@lib/auth'

interface AvatarProps {
  name: string
  color: string
  size?: number
  fontSize?: number
}

export function Avatar({ name, color, size = 30, fontSize = 12 }: AvatarProps) {
  return (
    <div
      style={{
        width: size, height: size, borderRadius: '50%',
        background: color, display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontSize, fontWeight: 600,
        color: '#fff', flexShrink: 0,
      }}
    >
      {initials(name)}
    </div>
  )
}
