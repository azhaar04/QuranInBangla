import AppShell from '../components/layout/AppShell'

export default function ComingSoonPage({ title }) {
  return (
    <AppShell title={title}>
      <div className="p-8">
        <p className="text-muted">শীঘ্রই আসছে...</p>
      </div>
    </AppShell>
  )
}
