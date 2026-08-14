import Sidebar from './Sidebar'
import Topbar from './Topbar'

export default function AppShell({ title, subtitle, actions, children }) {
  return (
    <div className="flex h-svh bg-page">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar title={title} subtitle={subtitle} actions={actions} />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  )
}
