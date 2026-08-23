import { useEffect } from 'react'

export default function Modal({ open, onClose, children, className = '', dismissible = true }) {
  useEffect(() => {
    if (!open || !dismissible) return
    function onKeyDown(e) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, dismissible, onClose])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-6 backdrop-blur-sm"
      onClick={dismissible ? onClose : undefined}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className={`max-h-[90vh] w-full overflow-y-auto rounded-[18.667px] border-[1.333px] border-modal-border bg-white shadow-modal ${className}`}
      >
        {children}
      </div>
    </div>
  )
}
