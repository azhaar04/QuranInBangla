const VARIANTS = {
  success: 'bg-status-success-bg text-status-success-text',
  warning: 'bg-status-warning-bg text-status-warning-text',
  neutral: 'bg-avatar-neutral-bg text-label',
}

export default function Badge({ variant = 'neutral', children, className = '' }) {
  return (
    <span
      className={`inline-flex h-8 min-w-[104px] items-center justify-center rounded-full px-4 text-[13.333px] font-semibold whitespace-nowrap ${VARIANTS[variant]} ${className}`}
    >
      {children}
    </span>
  )
}
