import React from 'react'

type Stat = { label: string; value: string | number | null | undefined }

export default function Stats({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {stats.map((s, i) => (
        <div key={i} className="rounded-md border p-3 bg-white">
          <div className="text-xs text-gray-500">{s.label}</div>
          <div className="text-lg font-semibold">{s.value ?? '-'}</div>
        </div>
      ))}
    </div>
  )
}


