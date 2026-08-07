import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(username, password)
      navigate('/')
    } catch {
      setError('Invalid username or password.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-svh flex items-center justify-center bg-neutral-100">
      <form
        onSubmit={handleSubmit}
        className="flex w-80 flex-col gap-3 rounded-lg border border-neutral-200 bg-white p-8"
      >
        <h1 className="mb-2 text-xl font-semibold text-neutral-900">QuranInBangla</h1>
        <label className="flex flex-col gap-1 text-sm text-neutral-600">
          Username
          <input
            className="rounded border border-neutral-300 px-3 py-2 text-neutral-900 focus:border-emerald-700 focus:outline-none"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
        </label>
        <label className="flex flex-col gap-1 text-sm text-neutral-600">
          Password
          <input
            type="password"
            className="rounded border border-neutral-300 px-3 py-2 text-neutral-900 focus:border-emerald-700 focus:outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="mt-2 rounded bg-emerald-800 py-2 text-sm font-medium text-white hover:bg-emerald-900 disabled:opacity-60"
        >
          {submitting ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}
