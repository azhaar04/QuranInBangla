import Sidebar from './Sidebar'
import Topbar from './Topbar'

export default function AppShell({ title, children }) {
  return (
    <div className="flex h-svh bg-page">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar title={title} />
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  )
}
