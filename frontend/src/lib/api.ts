let BASE: string = (import.meta.env.VITE_API_BASE as string) || '/api'

export function setApiBase(base: string) {
  if (!base) return
  BASE = base.replace(/\/$/, '')
}

export function getApiBase() {
  return BASE
}

type HeadersInit = Record<string, string>

export async function extractRaw(url: string, headers: HeadersInit = {}) {
  const res = await fetch(`${BASE}/api/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) throw Object.assign(new Error('request failed'), { status: res.status })
  return res.json()
}

export async function mapToRU(url: string, headers: HeadersInit = {}) {
  const res = await fetch(`${BASE}/api/map/rentals-united`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) throw Object.assign(new Error('request failed'), { status: res.status })
  return res.json()
}

export async function robotsCheck(url: string) {
  const res = await fetch(`${BASE}/robots-check?url=${encodeURIComponent(url)}`, { method: 'GET' })
  if (!res.ok) throw Object.assign(new Error('request failed'), { status: res.status })
  return res.json()
}

export async function health() {
  const res = await fetch(`${BASE}/healthz`)
  if (!res.ok) throw Object.assign(new Error('request failed'), { status: res.status })
  return res.json()
}
