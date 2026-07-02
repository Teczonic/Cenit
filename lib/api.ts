const getBase = () => {
  if (typeof window === 'undefined') return ''
  return window.location.hostname === 'localhost' ? 'http://localhost:8000' : ''
}

export async function apiFetch<T>(
  method: string,
  path: string,
  body?: unknown,
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(getBase() + path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { detail?: string }
    throw new Error(err.detail ?? String(res.status))
  }

  return res.json() as Promise<T>
}
