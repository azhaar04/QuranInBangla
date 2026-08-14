import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, LogIn, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import Card from '../components/ui/Card'
import Logo from '../components/ui/Logo'
import TextField from '../components/ui/TextField'
import Button from '../components/ui/Button'
import Alert from '../components/ui/Alert'

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
      setError('ইউজারনেম অথবা পাসওয়ার্ড সঠিক নয়।')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-3 bg-brand-dark px-4 py-5">
      <Card className="w-full max-w-md shadow-login-card">
        <div className="flex flex-col items-center gap-2 bg-brand-dark px-8 py-5">
          <Logo size={48} />
          <h1 className="text-center text-[26.67px] leading-none font-medium tracking-[0.4px]">
            <span className="text-gold">Quran</span>{' '}
            <span className="text-white">in</span>{' '}
            <span className="text-gold">Bangla</span>
          </h1>
          <span className="flex h-9 w-[278.84px] items-center justify-center rounded-full border-[1.33px] border-gold text-center text-[14px] leading-none font-medium tracking-[0.67px] text-gold">
            Translation Management System
          </span>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3 bg-cream px-8 py-5">
          <div className="text-center">
            <h2 className="text-[28px] leading-none font-medium text-heading">স্বাগতম</h2>
            <p className="mt-1 text-[17.33px] leading-none font-normal text-center text-muted">
              আপনার অ্যাকাউন্টে প্রবেশ করুন
            </p>
          </div>

          <TextField
            label="ইউজারনেম"
            icon={User}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />

          <div className="flex flex-col gap-2">
            <TextField
              label="পাসওয়ার্ড"
              icon={Lock}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <div className="flex justify-end">
              <a href="#" className="text-[16.67px] leading-none font-normal text-link hover:underline">
                পাসওয়ার্ড ভুলে গেছেন?
              </a>
            </div>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button type="submit" disabled={submitting} className="w-full">
            <LogIn className="h-4 w-4" />
            {submitting ? 'প্রবেশ করা হচ্ছে...' : 'প্রবেশ করুন'}
          </Button>

          <Alert>
            এই সিস্টেমটি শুধুমাত্র অনুমোদিত অ্যাডমিনের জন্য সংরক্ষিত। অননুমোদিত প্রবেশের
            চেষ্টা নিষিদ্ধ।
          </Alert>
        </form>
      </Card>
      <p className="text-center text-[14.67px] leading-none font-normal text-white">
        © 2026 QuraninBangla.com — All Rights Reserved
      </p>
    </div>
  )
}
