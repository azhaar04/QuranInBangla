const VARIANTS = {
  primary: 'bg-brand-dark text-white hover:bg-brand-dark/90',
  ghost: 'bg-transparent text-brand-dark hover:bg-black/5',
  success: 'bg-status-success-bg text-status-success-text hover:bg-status-success-bg/70',
}

export default function Button({
  variant = 'primary',
  className = '',
  children,
  ...props
}) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors disabled:opacity-60 disabled:cursor-not-allowed ${VARIANTS[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
