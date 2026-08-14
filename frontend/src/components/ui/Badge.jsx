const VARIANTS = {
  final: 'bg-brand-dark text-white',
  draft: 'bg-gold/20 text-gold',
}

export default function Badge({ variant = 'draft', children, className = '' }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${VARIANTS[variant]} ${className}`}
    >
      {children}
    </span>
  )
}
