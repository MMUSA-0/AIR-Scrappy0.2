import React from 'react'
import Badge from './Badge'

type Props = { data: any }

export default function ResultSummary({ data }: Props) {
  if (!data) return null
  const title = data.property_name || data.title || '-'
  const address = data.address?.full || [data.address?.city, data.address?.country].filter(Boolean).join(', ') || '-'
  const bedrooms = data.bedrooms ?? '-'
  const bathrooms = data.bathrooms ?? '-'
  const guests = data.max_guests ?? '-'
  const price = data.base_price ? `${data.base_price} ${data.currency || ''}` : '-'
  const photos = Array.isArray(data.photos) ? data.photos.length : 0
  const roomType = data.room_type || data.room_type_raw
  const propertyType = data.property_type || data.property_type_raw

  return (
    <div className="border rounded-md p-3 bg-white">
      <div className="font-medium mb-2">Summary</div>
      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-2 text-sm">
        <div><span className="text-gray-500">Title:</span> {title}</div>
        <div><span className="text-gray-500">Address:</span> {address}</div>
        <div><span className="text-gray-500">Bedrooms:</span> {bedrooms}</div>
        <div><span className="text-gray-500">Bathrooms:</span> {bathrooms}</div>
        <div><span className="text-gray-500">Max guests:</span> {guests}</div>
        <div><span className="text-gray-500">Photos:</span> {photos}</div>
        <div><span className="text-gray-500">Base price:</span> {price}</div>
      </div>
      <div className="mt-2 flex flex-wrap gap-2">
        {propertyType && <Badge color="blue">{String(propertyType)}</Badge>}
        {roomType && <Badge color="green">{String(roomType)}</Badge>}
        {data.host?.superhost && <Badge color="red">Superhost</Badge>}
      </div>
    </div>
  )
}


