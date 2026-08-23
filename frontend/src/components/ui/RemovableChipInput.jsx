import { useState } from 'react'
import { X } from 'lucide-react'

export default function RemovableChipInput({
  value = [],
  onChange,
  placeholder = 'নতুন শব্দ যোগ করুন…',
}) {
  const [draft, setDraft] = useState('')

  function addChip() {
    const text = draft.trim()
    if (!text) return
    onChange([...value, text])
    setDraft('')
  }

  function removeChip(index) {
    onChange(value.filter((_, i) => i !== index))
  }

  return (
    <div className="flex min-h-[73.333px] flex-wrap items-center gap-2 rounded-[10.667px] border-[1.333px] border-border-subtle bg-surface-subtle p-3">
      {value.map((word, index) => (
        <span
          key={`${word}-${index}`}
          className="inline-flex h-[49.333px] items-center gap-2 rounded-full border-[1.333px] border-border-subtle bg-white pl-4 pr-2"
        >
          <span className="font-arabic text-[18.667px] text-heading">{word}</span>
          <button
            type="button"
            onClick={() => removeChip(index)}
            className="flex h-[21.333px] w-[21.333px] shrink-0 items-center justify-center rounded-full bg-avatar-neutral-bg text-muted-2 hover:bg-border-subtle"
            aria-label={`${word} মুছে ফেলুন`}
          >
            <X className="h-[13.333px] w-[13.333px]" />
          </button>
        </span>
      ))}
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            addChip()
          }
        }}
        onBlur={addChip}
        placeholder={`⁦${placeholder}⁩`}
        dir="rtl"
        className="min-w-[140px] flex-1 bg-transparent font-arabic text-[18.667px] text-heading placeholder:text-left placeholder:font-sans placeholder:text-[15.333px] placeholder:text-input-text focus:outline-none"
      />
    </div>
  )
}
