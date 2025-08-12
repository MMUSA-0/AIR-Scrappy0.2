export type RunRecord = {
  id: string
  action: 'extract' | 'map'
  url: string
  startedAt: number
  endedAt: number
  status: 'ok' | 'error'
  httpStatus?: number
  durationMs: number
}


