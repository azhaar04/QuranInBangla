import { useEffect, useMemo, useState } from 'react'
import AppShell from '../components/layout/AppShell'
import StatBadge from '../components/ui/StatBadge'
import apiClient from '../api/client'
import { toBanglaNumeral } from '../utils/numerals'

function SurahBadge({ number }) {
  return (
    <span className="flex h-[34.667px] min-w-[34.667px] shrink-0 items-center justify-center rounded-[9.333px] bg-brand-dark px-2 text-[16px] font-semibold text-gold">
      {toBanglaNumeral(number)}
    </span>
  )
}

function RukuPill({ ruku }) {
  return (
    <span className="inline-flex h-[38.667px] items-center justify-center rounded-full border border-ruku-pill-border bg-ruku-pill-bg px-4 text-[15.333px] font-medium text-ruku-pill-text">
      R{ruku.surah_ruku_number} · {toBanglaNumeral(ruku.first_ayah_number)}:{toBanglaNumeral(ruku.last_ayah_number)}
    </span>
  )
}

const CELL_CLASS = 'flex min-w-0 items-center px-6 py-5'

function SurahRukuRow({ surah, rukus, isLast }) {
  const cellClass = `${CELL_CLASS} ${isLast ? '' : 'border-b-[1.333px] border-divider'}`
  return (
    <>
      <div className={cellClass}>
        <div className="flex items-center gap-3">
          <SurahBadge number={surah.number} />
          <span className="whitespace-nowrap text-[17.333px] font-medium text-heading">{surah.name_bangla}</span>
        </div>
      </div>
      <div className={cellClass}>
        <span className="text-[16.667px] text-label">{toBanglaNumeral(rukus.length)}</span>
      </div>
      <div className={cellClass}>
        <div className="flex flex-wrap gap-2.5">
          {rukus.map((ruku) => (
            <RukuPill key={ruku.id} ruku={ruku} />
          ))}
        </div>
      </div>
    </>
  )
}

export default function RukuListPage() {
  const [surahs, setSurahs] = useState([])
  const [rukus, setRukus] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([apiClient.get('/surahs/'), apiClient.get('/rukus/')])
      .then(([surahsRes, rukusRes]) => {
        setSurahs(surahsRes.data)
        setRukus(rukusRes.data)
      })
      .finally(() => setLoading(false))
  }, [])

  const rukusBySurah = useMemo(() => {
    const grouped = new Map()
    for (const ruku of rukus) {
      const list = grouped.get(ruku.surah) || []
      list.push(ruku)
      grouped.set(ruku.surah, list)
    }
    for (const list of grouped.values()) {
      list.sort((a, b) => a.surah_ruku_number - b.surah_ruku_number)
    }
    return grouped
  }, [rukus])

  return (
    <AppShell
      title="রুকু সম্পন্নতা সূচি"
      subtitle="প্রতিটি সূরার রুকু ও শেষ আয়াত অনুযায়ী অগ্রগতি"
      actions={
        <>
          <StatBadge value={toBanglaNumeral(surahs.length)} label="সূরা" />
          <StatBadge value={toBanglaNumeral(rukus.length)} label="রুকু" />
        </>
      }
    >
      <div className="p-8">
        {loading ? (
          <p className="text-muted">লোড হচ্ছে...</p>
        ) : (
          <div className="overflow-hidden rounded-2xl border border-header-line bg-white">
            <div className="grid grid-cols-[auto_auto_1fr]">
              <div className="border-b-[1.333px] border-header-line bg-surface-subtle-3 px-6 py-4 text-[15.333px] font-semibold text-label">
                সূরা
              </div>
              <div className="border-b-[1.333px] border-header-line bg-surface-subtle-3 px-6 py-4 text-[15.333px] font-semibold text-label">
                মোট রুকু
              </div>
              <div className="border-b-[1.333px] border-header-line bg-surface-subtle-3 px-6 py-4 text-[15.333px] font-semibold text-label">
                রুকু আয়াত
              </div>

              {surahs.map((surah, index) => (
                <SurahRukuRow
                  key={surah.id}
                  surah={surah}
                  rukus={rukusBySurah.get(surah.id) || []}
                  isLast={index === surahs.length - 1}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}
