export default function Topbar({ title, subtitle, actions }) {
  return (
    <header className="flex shrink-0 items-center justify-between gap-4 border-b-[1.333px] border-header-line bg-white px-[37.33px] py-4">
      <div>
        <h1 className="text-[22.667px] font-medium text-heading">{title}</h1>
        {subtitle && <p className="text-[16px] text-muted-2">{subtitle}</p>}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-3">{actions}</div>}
    </header>
  )
}
