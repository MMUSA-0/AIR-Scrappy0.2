import React, { useEffect, useMemo, useState } from 'react'
import { extractRaw, mapToRU, robotsCheck, health, getApiBase } from './lib/api'
import JsonPane from './components/JsonPane'
import UrlForm from './components/UrlForm'
import ResultSummary from './components/ResultSummary'
import Tabs from './components/Tabs'
import { useLocalStorage } from './lib/useLocalStorage'
import PhotoGrid from './components/PhotoGrid'
import AmenitiesList from './components/AmenitiesList'
import TopProgress from './components/TopProgress'
import RunHistory from './components/RunHistory'
import SummaryStats from './components/SummaryStats'
import type { RunRecord } from './lib/types'
import SideNav from './components/SideNav'

export default function App() {
  const [url, setUrl] = useLocalStorage<string>('ru-url', '')
  const [apiKey, setApiKey] = useLocalStorage<string>('ru-api-key', '')
  const [sendKey, setSendKey] = useLocalStorage<boolean>('ru-send-key', true)
  const [loading, setLoading] = useState(false)
  const [action, setAction] = useLocalStorage<'extract' | 'map'>('ru-action', 'extract')
  const [status, setStatus] = useState<string>('')
  const [result, setResult] = useState<any>(null)
  const [robots, setRobots] = useState<any>(null)
  const [backendInfo, setBackendInfo] = useState<any>(null)
  const [runs, setRuns] = useLocalStorage<RunRecord[]>('ru-runs', [])

  const headers = useMemo(() => (sendKey && apiKey ? { 'X-API-Key': apiKey } : {}), [sendKey, apiKey])

  const handle = async (action: 'extract' | 'map') => {
    setLoading(true)
    setStatus('')
    setResult(null)
    const t0 = performance.now()
    try {
      const data = action === 'extract' ? await extractRaw(url, headers) : await mapToRU(url, headers)
      setResult(data)
      const ms = Math.round(performance.now() - t0)
      setStatus(`OK in ${ms} ms`)
      setRuns(prev => [...prev, { id: crypto.randomUUID(), action, url, startedAt: t0, endedAt: performance.now(), status: 'ok', durationMs: ms }])
    } catch (err: any) {
      const ms = Math.round(performance.now() - t0)
      setStatus(`Error (${err?.status || '??'}) in ${ms} ms`)
      setRuns(prev => [...prev, { id: crypto.randomUUID(), action, url, startedAt: t0, endedAt: performance.now(), status: 'error', httpStatus: err?.status, durationMs: ms }])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Fetch backend health once
    ;(async () => {
      try { setBackendInfo(await health()) } catch {}
    })()
  }, [])

  useEffect(() => {
    // Fetch robots preview when URL changes
    const u = url.trim()
    if (!u) { setRobots(null); return }
    const ctrl = new AbortController()
    const id = setTimeout(async () => {
      try { setRobots(await robotsCheck(u)) } catch { setRobots(null) }
    }, 400)
    return () => { clearTimeout(id); ctrl.abort() }
  }, [url])

  return (
    <div className="min-h-screen bg-gray-50">
      <TopProgress active={loading} />
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-blue-600 text-white grid place-items-center font-bold">RU</div>
            <div>
              <h1 className="text-lg font-semibold">AIR-scrappy — Admin Console</h1>
              <p className="text-xs text-gray-500">Single-page admin • API: {getApiBase()}</p>
            </div>
          </div>
          <div className="text-xs text-gray-500">{backendInfo ? `Backend OK • browser: ${backendInfo.browser}` : 'Checking backend…'}</div>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="hidden lg:block lg:col-span-3">
            <SideNav
              items={[
                { id: 'controls', label: 'Controls' },
                { id: 'summary', label: 'Summary' },
                { id: 'photos', label: 'Photos' },
                { id: 'amenities', label: 'Amenities' },
                { id: 'output', label: 'Output (JSON)' },
                { id: 'stats', label: 'Stats' },
                { id: 'history', label: 'Run history' },
                { id: 'notes', label: 'Notes' },
              ]}
            />
          </div>
          <div className="lg:col-span-9 space-y-6">
            <section id="controls" className="bg-white rounded-lg border p-4">
              <UrlForm
                url={url}
                setUrl={setUrl}
                apiKey={apiKey}
                setApiKey={setApiKey}
                sendKey={sendKey}
                setSendKey={setSendKey}
                onExtract={() => handle('extract')}
                onMap={() => handle('map')}
                loading={loading}
                action={action}
                setAction={setAction}
              />
              <div className="mt-3 text-sm text-gray-500">{status}</div>
              {robots && (
                <div className="mt-3 text-xs bg-yellow-50 border border-yellow-200 rounded p-3">
                  <div className="font-medium mb-1">Robots.txt preview</div>
                  <div className="grid md:grid-cols-3 gap-2">
                    <div><span className="text-gray-500">URL:</span> {robots.robots_url || '-'}</div>
                    <div><span className="text-gray-500">Status:</span> {robots.status || '-'}</div>
                    <div className="truncate"><span className="text-gray-500">Snippet:</span> {robots.snippet || robots.error || '-'}</div>
                  </div>
                </div>
              )}
            </section>

            <section id="summary" className="space-y-4">
              <ResultSummary data={result} />
            </section>

            <section id="photos" className="space-y-4">
              <PhotoGrid photos={result?.photos} />
            </section>

            <section id="amenities" className="space-y-4">
              <AmenitiesList amenities={result?.amenities} amenitiesRaw={result?.amenities_raw} />
            </section>

            <section id="output" className="space-y-4">
              <Tabs
                items={[{
                  id: 'json',
                  label: 'JSON',
                  content: <JsonPane data={result} title="Output" />
                }]}
                initialId="json"
              />
            </section>

            <section id="stats" className="space-y-4">
              <SummaryStats runs={runs} />
            </section>

            <section id="history" className="space-y-4">
              <RunHistory runs={runs.slice().reverse()} onClear={() => setRuns([])} />
            </section>

            <section id="notes" className="space-y-4">
              <div className="border rounded-md p-3">
                <div className="font-medium mb-2">How to use</div>
                <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-1">
                  <li>Paste an Airbnb listing URL</li>
                <li>Choose Extract for raw data or Map (normalized)</li>
                  <li>Optionally provide an API key if backend requires it</li>
                </ol>
              </div>
              <div className="border rounded-md p-3">
                <div className="font-medium mb-2">Notes</div>
                <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                  <li>Respect site TOS/robots; avoid unauthorized scraping</li>
                  <li>Playwright may be used when needed for dynamic content</li>
                </ul>
              </div>
            </section>
          </div>
        </div>
      </main>
      <footer className="text-xs text-gray-400 py-6 text-center">© {new Date().getFullYear()} AIR-scrappy</footer>
    </div>
  )
}
