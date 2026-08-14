export default function Card({ className = '', children }) {
  return (
    <div className={`overflow-hidden rounded-2xl border border-border bg-white ${className}`}>
      {children}
    </div>
  )
}
