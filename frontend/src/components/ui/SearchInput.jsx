import { Search } from 'lucide-react'

export default function SearchInput({ className = '', inputClassName = '', ...props }) {
  return (
    <span className={`relative flex items-center ${className}`}>
      <Search className="pointer-events-none absolute left-3 h-4 w-4 text-muted-2" />
      <input
        className={`w-full rounded-[9.333px] border border-border-subtle bg-page py-2.5 pl-10 pr-3 text-sm text-heading placeholder:text-muted-2 focus:border-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-dark ${inputClassName}`}
        {...props}
      />
    </span>
  )
}
