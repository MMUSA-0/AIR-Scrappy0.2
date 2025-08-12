import React from 'react'

export default function AmenitiesList({ amenities, amenitiesRaw }: { amenities?: string[]; amenitiesRaw?: string[] }) {
  const list = (amenities && amenities.length > 0) ? amenities : (amenitiesRaw || [])
  if (!list || list.length === 0) return null
  return (
    <div className="border rounded-md p-3 bg-white">
      <div className="font-medium mb-2">Amenities {amenities && amenities.length ? '(normalized)' : '(raw)'}</div>
      <div className="flex flex-wrap gap-2">
        {list.map((a, i) => (
          <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">{a}</span>
        ))}
      </div>
    </div>
  )
}


