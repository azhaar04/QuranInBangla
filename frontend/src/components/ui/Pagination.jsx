import { ChevronLeft, ChevronRight } from 'lucide-react'
import { toBanglaNumeral } from '../../utils/numerals'

export default function Pagination({ page, totalPages, onChange, className = '' }) {
  if (totalPages <= 1) return null

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
