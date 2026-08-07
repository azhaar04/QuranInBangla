import { useEffect, useState } from 'react'
import apiClient from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function DashboardPage() {
  const { logout } = useAuth()
  const [status, setStatus] = useState('loading')
  const [surahCount, setSurahCount] = useState(null)

  useEffect(() => {
    apiClient
      .get('/surahs/')
      .then((res) => {
        const count = Array.isArray(res.data) ? res.data.length : res.data.count
        setSurahCount(count)
        setStatus('connected')
      })
      .catch(() => setStatus('error'))
  }, [])

  return (
    <div className="mx-auto max-w-3xl p-6">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-neutral-900">QuranInBangla</h1>
        <button
          type="button"
          onClick={logout}
          className="rounded border border-neutral-300 px-3 py-1.5 text-sm text-neutral-700 hover:bg-neutral-100"
        >
          Log out
        </button>
      </header>
      {status === 'loading' && <p className="text-neutral-600">Connecting to backend...</p>}
      {status === 'connected' && (
        <p className="text-emerald-800">Connected — {surahCount} surahs loaded from the API.</p>
      )}
      {status === 'error' && <p className="text-red-600">Could not reach the backend API.</p>}
    </div>
  )
}
