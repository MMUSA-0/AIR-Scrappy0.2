import React from 'react'

type Props = { data: unknown; title?: string }

export default function JsonPane({ data, title = 'Result' }: Props) {
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(data ? JSON.stringify(data, null, 2) : '')
    } catch {}
  }
  return (
    <div className="border rounded-md overflow-hidden">
      <div className="bg-gray-50 border-b px-3 py-2 text-sm font-medium flex items-center justify-between">
        <span>{title}</span>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500">{data ? 'JSON' : 'Empty'}</span>
          <button onClick={copy} className="text-xs text-blue-600 hover:underline">Copy</button>
        </div>
      </div>
      <pre className="bg-[#0b1021] text-gray-200 p-3 max-h-[520px] overflow-auto text-sm">
        {data ? JSON.stringify(data, null, 2) : 'No data'}
      </pre>
    </div>
  )
}
