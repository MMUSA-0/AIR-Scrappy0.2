import React, { useState } from 'react'
import { getApiBase, setApiBase } from '../lib/api'

type Props = {
  url: string
  setUrl: (v: string) => void
  apiKey: string
  setApiKey: (v: string) => void
  sendKey: boolean
  setSendKey: (v: boolean) => void
  onExtract: () => void
  onMap: () => void
  loading?: boolean
  action: 'extract' | 'map'
  setAction: (a: 'extract' | 'map') => void
}

export default function UrlForm({ url, setUrl, apiKey, setApiKey, sendKey, setSendKey, onExtract, onMap, loading, action, setAction }: Props) {
  const [apiBase, setApiBaseLocal] = useState<string>(getApiBase())

  const run = () => {
    if (action === 'extract') onExtract()
    else onMap()
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">Listing URL</label>
        <input
          type="text"
          placeholder="https://www.airbnb.com/rooms/..."
          value={url}
          onChange={e => setUrl(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') run() }}
          className="border rounded-md px-3 py-2 focus:outline-none focus:ring focus:ring-blue-200"
        />
      </div>
      <div className="grid md:grid-cols-3 gap-3">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium">API Base</label>
          <input
            type="text"
            placeholder="http://localhost:8000"
            value={apiBase}
            onChange={e => setApiBaseLocal(e.target.value)}
            onBlur={() => setApiBase(apiBase)}
            className="border rounded-md px-3 py-2 focus:outline-none focus:ring focus:ring-blue-200"
          />
          <span className="text-xs text-gray-500">Backend base URL</span>
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium">Auth</label>
          <div className="flex items-center gap-2">
            <input id="sendKey" type="checkbox" checked={sendKey} onChange={e => setSendKey(e.target.checked)} />
            <label htmlFor="sendKey" className="text-sm">Send API key</label>
          </div>
          <input
            type="text"
            placeholder="API key"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            disabled={!sendKey}
            className="border rounded-md px-3 py-2 disabled:bg-gray-100"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium">Action</label>
          <div className="inline-flex rounded-md shadow-sm border overflow-hidden">
            <button type="button" className={`px-3 py-2 ${action==='extract'?'bg-blue-600 text-white':'bg-white'}`} onClick={() => setAction('extract')}>Extract</button>
            <button type="button" className={`px-3 py-2 ${action==='map'?'bg-blue-600 text-white':'bg-white'}`} onClick={() => setAction('map')}>Map (normalized)</button>
          </div>
          <button
            onClick={run}
            disabled={!url || loading}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-md px-4 py-2 disabled:opacity-60"
          >{loading ? 'Working…' : action === 'extract' ? 'Extract (raw)' : 'Map (normalized)'}</button>
          <button
            type="button"
            onClick={() => setUrl('https://www.airbnb.com/rooms/780210484211628646')}
            className="text-xs text-gray-600 hover:underline text-left"
          >Try sample URL</button>
        </div>
      </div>
    </div>
  )
}
