export default function Tabs({ items, active, onChange, className = '' }) {
  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      {items.map((item) => {
        const isActive = item.key === active
        return (
          <button
            key={item.key}
            type="button"
            onClick={() => onChange(item.key)}
            className={`flex h-[45.333px] items-center justify-center rounded-full px-4 text-[16.667px] font-medium whitespace-nowrap transition-colors ${
              isActive
                ? 'bg-brand-dark text-white'
                : 'border border-border-subtle bg-white text-label hover:bg-page'
            }`}
          >
            {item.label}
          </button>
        )
      })}
    </div>
  )
}
