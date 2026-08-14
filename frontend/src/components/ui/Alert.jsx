import { Info } from 'lucide-react'

export default function Alert({ children, className = '' }) {
  return (
    <div
      className={`flex items-start gap-2 rounded-lg border-[1.33px] border-alert-border bg-alert-bg px-4 py-2.5 text-[16px] leading-[26.4px] font-normal text-alert-text ${className}`}
    >
      <Info className="mt-0.5 h-4 w-4 shrink-0 text-alert-text" />
      <div>{children}</div>
    </div>
  )
}
