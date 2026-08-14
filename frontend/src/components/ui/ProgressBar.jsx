export default function ProgressBar({
  value,
  fillClassName = 'bg-brand-dark',
  trackClassName = 'bg-progress-track-2',
  heightClassName = 'h-[5.333px]',
  className = '',
}) {
  const clamped = Math.min(100, Math.max(0, value))
  return (
    <div className={`w-full overflow-hidden rounded-full ${heightClassName} ${trackClassName} ${className}`}>
      <div className={`h-full rounded-full ${fillClassName}`} style={{ width: `${clamped}%` }} />
    </div>
  )
}
