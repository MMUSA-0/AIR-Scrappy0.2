import React from 'react'

type Item = { id: string; label: string }

export default function SideNav({ items, activeId }: { items: Item[]; activeId?: string }) {
  return (
    <nav className="hidden lg:block sticky top-4 self-start">
      <ul className="space-y-1 text-sm">
        {items.map((i) => (
          <li key={i.id}>
            <a
              href={`#${i.id}`}
              className={`block px-3 py-2 rounded hover:bg-gray-100 ${activeId === i.id ? 'bg-blue-50 text-blue-700' : 'text-gray-700'}`}
            >
              {i.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}


