import React from 'react'
import type { RunRecord } from '../lib/types'

export default function RunHistory({ runs, onClear }: { runs: RunRecord[]; onClear: () => void }) {
  if (!runs || runs.length === 0) return null
  return (
    <div className="border rounded-md bg-white">
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <div className="font-medium">Run history</div>
        <button className="text-xs text-gray-600 hover:underline" onClick={onClear}>Clear</button>
      </div>
      <div className="divide-y">
        {runs.slice(0, 10).map(r => (
          <div key={r.id} className="px-3 py-2 text-sm grid md:grid-cols-6 gap-2 items-center">
            <div className="truncate" title={r.url}>{r.url}</div>
            <div className="uppercase text-xs text-gray-500">{r.action}</div>
            <div className={r.status === 'ok' ? 'text-green-700' : 'text-red-700'}>{r.status}{r.httpStatus ? ` (${r.httpStatus})` : ''}</div>
            <div>{r.durationMs} ms</div>
            <div className="text-xs text-gray-500">{new Date(r.startedAt).toLocaleTimeString()}</div>
            <div className="text-xs text-gray-500">{new Date(r.endedAt).toLocaleTimeString()}</div>
          </div>
        ))}
      </div>
    </div>
  )
}


