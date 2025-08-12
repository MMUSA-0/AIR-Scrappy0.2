import React from 'react'

type Photo = { url: string; width?: number; height?: number; caption?: string }

export default function PhotoGrid({ photos }: { photos?: Photo[] }) {
  if (!photos || photos.length === 0) return null
  const toShow = photos.slice(0, 8)
  const remaining = photos.length - toShow.length
  return (
    <div className="border rounded-md p-3 bg-white">
      <div className="font-medium mb-2">Photos</div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {toShow.map((p, idx) => (
          <div key={idx} className="relative aspect-square overflow-hidden rounded bg-gray-100">
            {p.url ? (
              <img src={p.url} alt={p.caption || `Photo ${idx + 1}`} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full bg-gray-200" />
            )}
          </div>
        ))}
      </div>
      {remaining > 0 && (
        <div className="text-xs text-gray-500 mt-2">+{remaining} more</div>
      )}
    </div>
  )
}


