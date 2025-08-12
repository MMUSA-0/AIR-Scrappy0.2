import React, { useState } from 'react'

export type TabItem = { id: string; label: string; content: React.ReactNode }

export default function Tabs({ items, initialId }: { items: TabItem[]; initialId?: string }) {
  const [active, setActive] = useState<string>(initialId || (items[0]?.id ?? ''))
  const activeItem = items.find(i => i.id === active) || items[0]
  return (
    <div className="border rounded-md overflow-hidden bg-white">
      <div className="flex gap-1 border-b bg-gray-50 px-2">
        {items.map(i => (
          <button
            key={i.id}
            onClick={() => setActive(i.id)}
            className={`px-3 py-2 text-sm ${active === i.id ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600'}`}
          >
            {i.label}
          </button>
        ))}
      </div>
      <div className="p-3">
        {activeItem?.content}
      </div>
    </div>
  )
}


