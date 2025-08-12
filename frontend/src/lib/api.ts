let BASE: string = ((import.meta.env.VITE_API_BASE as string) || '').replace(/\/$/, '')
const API_PREFIX = '/api'

export function setApiBase(base: string) {
  if (!base) return
  // Treat '/api' as empty since endpoints already include the '/api' prefix
  const cleaned = base.trim()
  BASE = cleaned === '/api' || cleaned === '/api/' ? '' : cleaned.replace(/\/$/, '')
}

export function getApiBase() {
  return BASE
}

type HeadersInit = Record<string, string>

export async function extractRaw(url: string, headers: HeadersInit = {}) {
  const res = await fetch(`${BASE}${API_PREFIX}/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) throw Object.assign(new Error('request failed'), { status: res.status })
  return res.json()
}

export async function mapToRU(url: string, headers: HeadersInit = {}) {
  const res = await fetch(`${BASE}${API_PREFIX}/map/rentals-united`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) throw Object.assign(new Error('request failed'), { status: res.status })
  return res.json()
}

export function normalizeUrl(input: string): string {
  if (!input) return ''
  let s = String(input).trim()
  if (s.startsWith('@')) s = s.replace(/^@+/, '').trim()
  if ((s.startsWith('<') && s.endsWith('>')) || (s.startsWith('"') && s.endsWith('"'))) {
    s = s.slice(1, -1).trim()
  }
  while (s && ")].,".includes(s.slice(-1))) s = s.slice(0, -1)
  if (!/^https?:\/\//i.test(s)) s = 'https://' + s
  return s
}

export async function robotsCheck(url: string) {
  const res = await fetch(`${BASE}${API_PREFIX}/robots-check?url=${encodeURIComponent(url)}`, { method: 'GET' })
  if (!res.ok) throw Object.assign(new Error('request failed'), { status: res.status })
  return res.json()
}

export async function health() {
  const res = await fetch(`${BASE}${API_PREFIX}/healthz`)
  if (!res.ok) throw Object.assign(new Error('request failed'), { status: res.status })
  return res.json()
}
