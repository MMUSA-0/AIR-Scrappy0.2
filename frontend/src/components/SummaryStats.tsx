import React from 'react'
import type { RunRecord } from '../lib/types'

function percentile(values: number[], p: number) {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const idx = Math.min(sorted.length - 1, Math.max(0, Math.floor((p / 100) * sorted.length)))
  return sorted[idx]
}

export default function SummaryStats({ runs }: { runs: RunRecord[] }) {
  const last50 = runs.slice(-50)
  const durs = last50.map(r => r.durationMs)
  const success = last50.filter(r => r.status === 'ok').length
  const error = last50.length - success
  const p50 = Math.round(percentile(durs, 50))
  const p95 = Math.round(percentile(durs, 95))
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="rounded-md border p-3 bg-white">
        <div className="text-xs text-gray-500">Runs (last 50)</div>
        <div className="text-lg font-semibold">{last50.length}</div>
      </div>
      <div className="rounded-md border p-3 bg-white">
        <div className="text-xs text-gray-500">Success</div>
        <div className="text-lg font-semibold text-green-700">{success}</div>
      </div>
      <div className="rounded-md border p-3 bg-white">
        <div className="text-xs text-gray-500">Errors</div>
        <div className="text-lg font-semibold text-red-700">{error}</div>
      </div>
      <div className="rounded-md border p-3 bg-white">
        <div className="text-xs text-gray-500">Latency p50 / p95</div>
        <div className="text-lg font-semibold">{p50} / {p95} ms</div>
      </div>
    </div>
  )
}


