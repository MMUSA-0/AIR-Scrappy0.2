import React from 'react'

export default function TopProgress({ active }: { active: boolean }) {
  if (!active) return null
  return (
    <div className="fixed top-0 left-0 right-0 h-1 z-50">
      <div className="h-full bg-gradient-to-r from-blue-400 via-blue-600 to-blue-400 animate-[progress_1.2s_linear_infinite]" />
      <style>{`@keyframes progress {0%{transform:translateX(-100%)}50%{transform:translateX(0%)}100%{transform:translateX(100%)}}`}</style>
    </div>
  )
}


