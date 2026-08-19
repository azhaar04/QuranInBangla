export default function StatBadge({ value, label }) {
  return (
    <div className="flex h-[70.667px] min-w-[72px] flex-col items-center justify-center gap-0.5 rounded-xl bg-surface-subtle px-4">
      <span className="text-[20px] font-bold text-brand-dark">{value}</span>
      <span className="text-[13.333px] text-muted-2">{label}</span>
    </div>
  )
}
