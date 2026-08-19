import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import Badge from '../components/ui/Badge'
import apiClient from '../api/client'
import { toBanglaNumeral } from '../utils/numerals'

const TARGET_WORDS_PER_PAGE = 130

const FONT_SIZES = {
  14: { word: 30, gloss: 13, translation: 15.333 },
  16: { word: 34, gloss: 14, translation: 16.667 },
}

const STATUS_BADGE = {
  final: { variant: 'success', label: 'Final' },
  draft: { variant: 'warning', label: 'Draft' },
}

function paginateAyahs(ayahs, targetWords) {
  const pages = []
  let current = []
  let currentWords = 0

  for (const ayah of ayahs) {
    const wordCount = ayah.word_occurrences.length
    if (current.length > 0 && currentWords + wordCount > targetWords) {
      pages.push(current)
      current = []
      currentWords = 0
    }
    current.push(ayah)
    currentWords += wordCount
  }
  if (current.length > 0) pages.push(current)

  return pages
}

function AyahNumberBadge({ number }) {
  return (
    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[9.333px] bg-brand-dark text-[15.333px] font-semibold text-white">
      {toBanglaNumeral(number)}
    </span>
  )
}

function AyahCard({ ayah, fontSize }) {
  const sizes = FONT_SIZES[fontSize]
  const badge = STATUS_BADGE[ayah.status]

  return (
    <div className="rounded-2xl border border-header-line bg-white p-8">
      <div className="flex items-center gap-3">
        <AyahNumberBadge number={ayah.ayah_number} />
        <Badge variant={badge.variant}>{badge.label}</Badge>
      </div>

      <div dir="rtl" className="mt-6 flex flex-wrap gap-x-8 gap-y-5">
        {ayah.word_occurrences.map((occurrence) => (
          <div key={occurrence.id} className="flex flex-col items-center gap-1.5">
            <span
              className="font-arabic text-heading"
              style={{ fontSize: `${sizes.word}px`, lineHeight: 1.8 }}
            >
              {occurrence.raw_text}
            </span>
            <span className="text-muted-2" style={{ fontSize: `${sizes.gloss}px` }}>
              {occurrence.meaning_text || '—'}
            </span>
          </div>
        ))}
      </div>

      {ayah.translation_text && (
        <p className="mt-7 leading-relaxed text-heading" style={{ fontSize: `${sizes.translation}px` }}>
          <span className="font-semibold text-link">অনুবাদ: </span>
          {ayah.translation_text}
        </p>
      )}
    </div>
  )
}

export default function SurahAyahPage() {
  const { surahNumber } = useParams()
  const [surah, setSurah] = useState(null)
  const [ayahs, setAyahs] = useState([])
  const [loading, setLoading] = useState(true)
  const [pageIndex, setPageIndex] = useState(0)
  const [fontSize, setFontSize] = useState(14)
  const topRef = useRef(null)

  useEffect(() => {
    setLoading(true)
    setPageIndex(0)
    Promise.all([
      apiClient.get(`/surahs/${surahNumber}/`),
      apiClient.get(`/surahs/${surahNumber}/ayahs/`),
    ])
      .then(([surahRes, ayahsRes]) => {
        setSurah(surahRes.data)
        setAyahs(ayahsRes.data)
      })
      .finally(() => setLoading(false))
  }, [surahNumber])

  const pages = useMemo(() => paginateAyahs(ayahs, TARGET_WORDS_PER_PAGE), [ayahs])
  const currentAyahs = pages[pageIndex] || []
  const totalPages = pages.length

  function goToPage(index) {
    setPageIndex(index)
    topRef.current?.scrollIntoView({ block: 'start' })
  }

  return (
    <AppShell
      title={
        <span className="inline-flex items-center gap-2">
          <Link to="/surahs" className="text-muted-2 hover:text-heading">
            সূরার তালিকা
          </Link>
          {surah && (
            <>
              <span className="text-muted-2">›</span>
              <span className="text-heading">
                {toBanglaNumeral(surah.number)} · {surah.name_bangla}
              </span>
            </>
          )}
        </span>
      }
      actions={
        <div className="flex items-center gap-2.5">
          <span className="text-[14.667px] text-muted-2">ফন্ট সাইজ</span>
          <div className="flex overflow-hidden rounded-[9.333px] border border-border-subtle">
            {[14, 16].map((size) => (
              <button
                key={size}
                type="button"
                onClick={() => setFontSize(size)}
                className={`flex h-10 w-11 items-center justify-center text-[14.667px] font-medium transition-colors ${
                  fontSize === size
                    ? 'bg-brand-dark text-white'
                    : 'bg-white text-label hover:bg-page'
                }`}
              >
                {size}
              </button>
            ))}
          </div>
        </div>
      }
    >
      <div ref={topRef} className="p-8">
        {loading ? (
          <p className="text-muted">লোড হচ্ছে...</p>
        ) : currentAyahs.length === 0 ? (
          <p className="text-muted">কোনো আয়াত পাওয়া যায়নি।</p>
        ) : (
          <>
            <div className="flex flex-col gap-6">
              {currentAyahs.map((ayah) => (
                <AyahCard key={ayah.id} ayah={ayah} fontSize={fontSize} />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="mt-8 flex flex-col items-center gap-3">
                <p className="text-[14.667px] text-muted-2">
                  পৃষ্ঠা {toBanglaNumeral(pageIndex + 1)} / {toBanglaNumeral(totalPages)}
                </p>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => goToPage(pageIndex - 1)}
                    disabled={pageIndex <= 0}
                    className="flex items-center gap-1.5 rounded-full bg-brand-dark px-6 py-3 text-[15.333px] font-medium text-white transition-opacity disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <ChevronLeft className="h-4 w-4" />
                    পূর্ববর্তী পৃষ্ঠা
                  </button>
                  <button
                    type="button"
                    onClick={() => goToPage(pageIndex + 1)}
                    disabled={pageIndex >= totalPages - 1}
                    className="flex items-center gap-1.5 rounded-full bg-brand-dark px-6 py-3 text-[15.333px] font-medium text-white transition-opacity disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    পরবর্তী পৃষ্ঠা
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </AppShell>
  )
}
