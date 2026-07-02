'use client'

import React, { useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@lib/context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const router    = useRouter()
  const userRef   = useRef<HTMLInputElement>(null)
  const passRef   = useRef<HTMLInputElement>(null)
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit() {
    const u = userRef.current?.value.trim() ?? ''
    const p = passRef.current?.value ?? ''
    setErr('')
    setLoading(true)
    try {
      await login(u, p)
      router.push('/kanban')
    } catch (e: unknown) {
      setErr((e as Error).message || 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  const inp: React.CSSProperties = {
    width: '100%', background: 'var(--navy3)', border: '1px solid var(--border2)',
    borderRadius: 'var(--radius2)', padding: '10px 14px', color: 'var(--text)',
    fontSize: 14, marginBottom: 16,
  }

  return (
    <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--navy)' }}>
      <div style={{ background: 'var(--navy2)', border: '1px solid var(--border2)', borderRadius: 20, padding: '2.5rem 2rem', width: '100%', maxWidth: 380, animation: 'fadeUp .5s ease both' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '2rem' }}>
          <div style={{ width: 40, height: 40, background: 'var(--accent)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, fontWeight: 600, color: '#fff' }}>C</div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 600, letterSpacing: '-.5px' }}>Cenit</div>
            <div style={{ fontSize: 13, color: 'var(--text2)', marginTop: 1 }}>Team Backlog Manager</div>
          </div>
        </div>

        <label style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 6, display: 'block', letterSpacing: '.5px', textTransform: 'uppercase' }}>Usuario</label>
        <input ref={userRef} style={inp} placeholder="tu usuario" autoComplete="username"
          onKeyDown={e => e.key === 'Enter' && passRef.current?.focus()} />

        <label style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 6, display: 'block', letterSpacing: '.5px', textTransform: 'uppercase' }}>Contraseña</label>
        <input ref={passRef} type="password" style={inp} placeholder="••••••••" autoComplete="current-password"
          onKeyDown={e => e.key === 'Enter' && submit()} />

        <button onClick={submit} disabled={loading}
          style={{ width: '100%', background: 'var(--accent)', color: '#fff', borderRadius: 'var(--radius2)', padding: 11, fontSize: 14, fontWeight: 500, cursor: 'pointer', opacity: loading ? 0.7 : 1 }}>
          {loading ? 'Ingresando…' : 'Ingresar'}
        </button>

        {err && <div style={{ fontSize: 13, color: 'var(--red)', marginTop: 8 }}>{err}</div>}

        <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border)', fontSize: 12, color: 'var(--text3)' }}>
          Demo: <b style={{ color: 'var(--text2)' }}>fidel</b> / <b style={{ color: 'var(--text2)' }}>fidel123</b>
          &nbsp;&nbsp;|&nbsp;&nbsp;
          <b style={{ color: 'var(--text2)' }}>lorena</b> / <b style={{ color: 'var(--text2)' }}>lorena123</b>
        </div>
      </div>
    </div>
  )
}
