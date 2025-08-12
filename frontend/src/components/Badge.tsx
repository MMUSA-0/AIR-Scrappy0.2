import React from 'react'

export default function Badge({ children, color = 'gray' }: { children: React.ReactNode; color?: 'gray' | 'blue' | 'green' | 'red' }) {
  const colors: Record<string, string> = {
    gray: 'bg-gray-100 text-gray-700',
    blue: 'bg-blue-100 text-blue-700',
    green: 'bg-green-100 text-green-700',
    red: 'bg-red-100 text-red-700',
  }
  return <span className={`inline-block text-xs px-2 py-1 rounded ${colors[color]}`}>{children}</span>
}


