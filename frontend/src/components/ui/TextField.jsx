import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'

export default function TextField({
  label,
  icon: Icon,
  type = 'text',
  className = '',
  ...props
}) {
  const [revealed, setRevealed] = useState(false)
  const isPassword = type === 'password'
  const inputType = isPassword && revealed ? 'text' : type

  return (
    <label className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <span className="text-[16.67px] leading-none font-medium text-label">{label}</span>
      )}
      <span className="relative flex items-center">
        {Icon && (
          <Icon className="pointer-events-none absolute left-3 h-4 w-4 text-neutral-400" />
        )}
        <input
          type={inputType}
          className={`w-full rounded-lg border border-transparent bg-input-bg py-2.5 text-sm text-input-text placeholder:text-neutral-500 focus:border-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-dark ${
            Icon ? 'pl-10' : 'pl-3'
          } ${isPassword ? 'pr-10' : 'pr-3'}`}
          {...props}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setRevealed((r) => !r)}
            className="absolute right-3 text-neutral-400 hover:text-neutral-600"
            tabIndex={-1}
          >
            {revealed ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        )}
      </span>
    </label>
  )
}
