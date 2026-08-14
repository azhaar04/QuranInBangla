export default function Topbar({ title }) {
  return (
    <header className="flex h-[82.67px] shrink-0 items-center border-b-[1.333px] border-header-line bg-white px-[37.33px]">
      <h1 className="text-[22.667px] font-medium text-heading">{title}</h1>
    </header>
  )
}
