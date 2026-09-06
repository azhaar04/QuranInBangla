import { ChevronLeft, ChevronRight } from 'lucide-react'
import { toBanglaNumeral } from '../../utils/numerals'

function getPageNumbers(current, total, delta = 2) {
  const range = []
  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
      range.push(i)
    }
  }
  const withDots = []
  let last
  for (const i of range) {
    if (last !== undefined && i - last > 1) withDots.push(`gap-${i}`)
    withDots.push(i)
    last = i
  }
  return withDots
}

function PageButton({ active, disabled, children, onClick, ariaLabel }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      className={`flex h-[37.333px] w-[37.333px] shrink-0 items-center justify-center rounded-[9.333px] text-[16px] font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-40 ${
        active
          ? 'bg-brand-dark text-white'
          : 'border border-header-line bg-page text-label hover:bg-white'
      }`}
    >
      {children}
    </button>
  )
}

function NumberedPagination({ page, totalPages, onChange, className }) {
  const pages = getPageNumbers(page, totalPages)
  return (
    <div className={`flex items-center justify-end gap-2 ${className}`}>
      <PageButton disabled={page <= 1} onClick={() => onChange(page - 1)} ariaLabel="পূর্ববর্তী পৃষ্ঠা">
        <ChevronLeft className="h-4 w-4" />
      </PageButton>
      {pages.map((p) =>
        typeof p === 'string' ? (
          <span key={p} className="px-1 text-[16px] text-muted-2">
            …
          </span>
        ) : (
          <PageButton key={p} active={p === page} onClick={() => onChange(p)}>
            {toBanglaNumeral(p)}
          </PageButton>
        ),
      )}
      <PageButton disabled={page >= totalPages} onClick={() => onChange(page + 1)} ariaLabel="পরবর্তী পৃষ্ঠা">
        <ChevronRight className="h-4 w-4" />
      </PageButton>
    </div>
  )
}

export default function Pagination({ page, totalPages, onChange, variant = 'simple', className = '' }) {
  if (totalPages <= 1) return null

  if (variant === 'numbered') {
    return <NumberedPagination page={page} totalPages={totalPages} onChange={onChange} className={className} />
  }

  return (
    <div className={`flex items-center justify-between ${className}`}>
      <p className="text-[14.667px] text-muted-2">
        পৃষ্ঠা {toBanglaNumeral(page)} / {toBanglaNumeral(totalPages)}
      </p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onChange(page - 1)}
          disabled={page <= 1}
          aria-label="পূর্ববর্তী পৃষ্ঠা"
          className="flex h-9 w-9 items-center justify-center rounded-[9.333px] border border-border-subtle bg-white text-label transition-colors hover:bg-page disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={() => onChange(page + 1)}
          disabled={page >= totalPages}
          aria-label="পরবর্তী পৃষ্ঠা"
          className="flex h-9 w-9 items-center justify-center rounded-[9.333px] border border-border-subtle bg-white text-label transition-colors hover:bg-page disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
