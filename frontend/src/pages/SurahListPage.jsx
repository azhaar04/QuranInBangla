import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Grid2X2, List } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import SearchInput from '../components/ui/SearchInput'
import Tabs from '../components/ui/Tabs'
import ProgressBar from '../components/ui/ProgressBar'
import Badge from '../components/ui/Badge'
import apiClient from '../api/client'
import { toBanglaNumeral } from '../utils/numerals'

const STATUS_FILTERS = [
  { key: 'all', label: 'সব' },
  { key: 'complete', label: 'সম্পূর্ণ' },
  { key: 'in_progress', label: 'চলমান' },
  { key: 'not_started', label: 'বাকি' },
]

const PLACE_FILTERS = [
  { key: 'makkah', label: 'মক্কী' },
  { key: 'madinah', label: 'মদনী' },
]

const PLACE_LABEL = { makkah: 'মক্কী', madinah: 'মদনী' }

const STATUS_BADGE = {
  complete: { variant: 'success', label: 'সম্পন্ন' },
  in_progress: { variant: 'warning', label: 'চলমান' },
  not_started: { variant: 'neutral', label: 'বাকি' },
}

const PROGRESS_FILL = {
  complete: 'bg-progress-fill',
  in_progress: 'bg-gold',
  not_started: 'bg-transparent',
}

function SurahNumberBadge({ number, className = '' }) {
  return (
    <span
      className={`flex shrink-0 items-center justify-center rounded-full bg-avatar-neutral-bg font-semibold text-label ${className}`}
    >
      {toBanglaNumeral(number)}
    </span>
  )
}

const CELL_CLASS = 'flex min-w-0 items-center px-6 py-4'

function SurahRow({ surah, isLast }) {
  const badge = STATUS_BADGE[surah.status]
  const cellClass = `${CELL_CLASS} ${isLast ? '' : 'border-b-[1.333px] border-divider'} transition-colors group-hover:bg-page`
  return (
    <Link to={`/surahs/${surah.number}`} className="group contents">
      <div className={cellClass}>
        <div className="flex items-center gap-4">
          <SurahNumberBadge number={surah.number} className="h-[37.333px] w-[37.333px] text-[14.667px]" />
          <span className="w-24 shrink-0 text-center font-arabic text-[24px] text-heading">
            {surah.name_arabic}
          </span>
          <div className="whitespace-nowrap">
            <p className="text-[18px] font-medium text-heading">{surah.name_bangla}</p>
            <p className="text-[14.667px] text-muted-2">
              {toBanglaNumeral(surah.total_ayah)} আয়াত · {PLACE_LABEL[surah.revelation_place]}
            </p>
          </div>
        </div>
      </div>
      <div className={cellClass}>
        <div className="flex w-full min-w-0 items-center gap-3">
          <ProgressBar
            value={surah.progress_percent}
            fillClassName={PROGRESS_FILL[surah.status]}
            className="min-w-0 flex-1"
          />
          <span className="shrink-0 text-right text-[15.333px] font-medium text-label">
            {toBanglaNumeral(surah.progress_percent)}%
          </span>
        </div>
      </div>
      <div className={`${cellClass} justify-center`}>
        <Badge variant={badge.variant}>{badge.label}</Badge>
      </div>
    </Link>
  )
}

function SurahTable({ surahs }) {
  const headerClass =
    'border-b-[1.333px] border-header-line bg-surface-subtle-2 px-6 py-4 text-[14px] font-semibold tracking-[0.4px] text-muted-2 uppercase'
  return (
    <div className="overflow-hidden rounded-[13.333px] border border-header-line bg-white">
      <div className="grid grid-cols-[auto_1fr_auto]">
        <div className={`${headerClass} text-center`}>সূরা</div>
        <div className={headerClass}>অগ্রগতি</div>
        <div className={`${headerClass} text-center`}>অবস্থা</div>

        {surahs.map((surah, index) => (
          <SurahRow key={surah.id} surah={surah} isLast={index === surahs.length - 1} />
        ))}
      </div>
    </div>
  )
}

function SurahCard({ surah }) {
  const badge = STATUS_BADGE[surah.status]
  return (
    <Link
      to={`/surahs/${surah.number}`}
      className="block rounded-2xl border border-header-line bg-white p-5 transition-colors hover:bg-page"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <SurahNumberBadge number={surah.number} className="h-8 w-8 text-[13.333px]" />
          <div>
            <p className="text-[18px] font-medium text-heading">{surah.name_bangla}</p>
            <p className="text-[14.667px] text-muted-2">
              {toBanglaNumeral(surah.total_ayah)} আয়াত · {PLACE_LABEL[surah.revelation_place]}
            </p>
          </div>
        </div>
        <span className="font-arabic text-[24px] text-heading">{surah.name_arabic}</span>
      </div>
      <ProgressBar value={surah.progress_percent} fillClassName={PROGRESS_FILL[surah.status]} className="mt-4" />
      <div className="mt-3 flex items-center justify-between">
        <Badge variant={badge.variant}>{badge.label}</Badge>
        <span className="text-[15.333px] font-medium text-label">{toBanglaNumeral(surah.progress_percent)}%</span>
      </div>
    </Link>
  )
}

export default function SurahListPage() {
  const [surahs, setSurahs] = useState([])
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState('list')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [placeFilter, setPlaceFilter] = useState(null)

  useEffect(() => {
    apiClient
      .get('/surahs/')
      .then((res) => setSurahs(res.data))
      .finally(() => setLoading(false))
  }, [])

  const counts = useMemo(() => {
    const result = { all: surahs.length, complete: 0, in_progress: 0, not_started: 0, makkah: 0, madinah: 0 }
    for (const surah of surahs) {
      result[surah.status] += 1
      result[surah.revelation_place] += 1
    }
    return result
  }, [surahs])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return surahs.filter((surah) => {
      if (statusFilter !== 'all' && surah.status !== statusFilter) return false
      if (placeFilter && surah.revelation_place !== placeFilter) return false
      if (
        term &&
        !surah.name_bangla.toLowerCase().includes(term) &&
        !surah.name_english.toLowerCase().includes(term) &&
        !surah.name_arabic.includes(term)
      ) {
        return false
      }
      return true
    })
  }, [surahs, search, statusFilter, placeFilter])

  const totalAyah = useMemo(() => surahs.reduce((sum, surah) => sum + surah.total_ayah, 0), [surahs])

  return (
    <AppShell
      title="সূরার তালিকা"
      subtitle={
        surahs.length > 0
          ? `মোট ${toBanglaNumeral(surahs.length)}টি সূরা · ${toBanglaNumeral(totalAyah.toLocaleString('en-US'))} আয়াত`
          : undefined
      }
      actions={
        <>
          <SearchInput
            placeholder="সূরা খুঁজুন..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-[266.667px]"
          />
          <div className="flex h-[50.667px] overflow-hidden rounded-[9.333px] border border-border-subtle">
            <button
              type="button"
              onClick={() => setView('card')}
              aria-label="কার্ড ভিউ"
              className={`flex w-[52px] items-center justify-center transition-colors ${
                view === 'card' ? 'bg-brand-dark text-white' : 'bg-white text-label hover:bg-page'
              }`}
            >
              <Grid2X2 className="h-[18px] w-[18px]" />
            </button>
            <button
              type="button"
              onClick={() => setView('list')}
              aria-label="লিস্ট ভিউ"
              className={`flex w-[52px] items-center justify-center border-l border-border-subtle transition-colors ${
                view === 'list' ? 'bg-brand-dark text-white' : 'bg-white text-label hover:bg-page'
              }`}
            >
              <List className="h-[18px] w-[18px]" />
            </button>
          </div>
        </>
      }
    >
      <div className="flex items-center gap-3 border-b-[1.333px] border-header-line bg-white px-[37.33px] py-5">
        <Tabs
          items={STATUS_FILTERS.map((f) => ({ ...f, label: `${f.label} (${toBanglaNumeral(counts[f.key])})` }))}
          active={statusFilter}
          onChange={setStatusFilter}
        />
        <span className="h-[29.333px] w-[1.333px] shrink-0 bg-border-subtle" />
        <Tabs
          items={PLACE_FILTERS.map((f) => ({ ...f, label: `${f.label} (${toBanglaNumeral(counts[f.key])})` }))}
          active={placeFilter}
          onChange={(key) => setPlaceFilter(placeFilter === key ? null : key)}
        />
      </div>

      <div className="p-8">
        {loading ? (
          <p className="text-muted">লোড হচ্ছে...</p>
        ) : filtered.length === 0 ? (
          <p className="text-muted">কোনো সূরা পাওয়া যায়নি।</p>
        ) : view === 'list' ? (
          <SurahTable surahs={filtered} />
        ) : (
          <div className="grid grid-cols-3 gap-5">
            {filtered.map((surah) => (
              <SurahCard key={surah.id} surah={surah} />
            ))}
          </div>
        )}
      </div>
    </AppShell>
  )
}
