import { useEffect, useRef, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle2 } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import WordAnalysisModal from '../components/word/WordAnalysisModal'
import apiClient from '../api/client'
import { toBanglaNumeral } from '../utils/numerals'
import { autoResizeTextarea } from '../utils/textarea'

function WordGridItem({ occurrence, selected, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex flex-col items-center gap-1.5 rounded-xl border-[1.333px] px-3 py-2 transition-colors hover:border-progress-fill hover:bg-word-hover-bg ${
        selected ? 'border-progress-fill bg-word-hover-bg' : 'border-transparent'
      }`}
    >
      <span className="font-arabic text-heading" style={{ fontSize: '32px', lineHeight: 1.8 }}>
        {occurrence.raw_text}
      </span>
      <span className="text-[15.333px] font-semibold text-link">
        {occurrence.meaning_text || '—'}
      </span>
    </button>
  )
}

function StatusLegend({ assignedCount, unassignedCount }) {
  return (
    <div className="flex shrink-0 items-center gap-4">
      <span className="flex items-center gap-2 text-[14.667px] font-medium text-link">
        <span className="h-3 w-3 rounded-[4px] border-[1.333px] border-status-dot-border-green bg-alert-bg" />
        অনুবাদ দেওয়া হয়েছে ({toBanglaNumeral(assignedCount)})
      </span>
      <span className="flex items-center gap-2 text-[14.667px] font-medium text-muted-2">
        <span className="h-3 w-3 rounded-[4px] border-[1.333px] border-dashed border-status-dot-border-dashed bg-surface-subtle-3" />
        এখনো ফাঁকা ({toBanglaNumeral(unassignedCount)})
      </span>
    </div>
  )
}

export default function AyahWorkspacePage() {
  const { surahNumber, ayahNumber } = useParams()
  const location = useLocation()
  const verseKey = `${surahNumber}:${ayahNumber}`

  const backTo = {
    pathname: `/surahs/${surahNumber}`,
    search: location.state?.fromPage ? `?page=${location.state.fromPage}` : '',
  }
  const backState = location.state?.scrollToAyah
    ? { scrollToAyah: location.state.scrollToAyah }
    : undefined

  const [ayah, setAyah] = useState(null)
  const [surah, setSurah] = useState(null)
  const [loading, setLoading] = useState(true)
  const [translationText, setTranslationText] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [finalizing, setFinalizing] = useState(false)
  const [justSaved, setJustSaved] = useState(false)
  const [error, setError] = useState(null)
  const [selectedOccurrenceId, setSelectedOccurrenceId] = useState(null)

  const translationRef = useRef(null)
  const notesRef = useRef(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    setJustSaved(false)
    Promise.all([
      apiClient.get(`/ayahs/${verseKey}/`),
      apiClient.get(`/surahs/${surahNumber}/`),
    ])
      .then(([ayahRes, surahRes]) => {
        setAyah(ayahRes.data)
        setTranslationText(ayahRes.data.translation_text)
        setNotes(ayahRes.data.notes)
        setSurah(surahRes.data)
      })
      .finally(() => setLoading(false))
  }, [verseKey, surahNumber])

  useEffect(() => {
    autoResizeTextarea(translationRef.current, translationText)
  }, [translationText, loading])

  useEffect(() => {
    autoResizeTextarea(notesRef.current, notes)
  }, [notes, loading])

  const isDirty = ayah !== null && (translationText !== ayah.translation_text || notes !== ayah.notes)

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      const res = await apiClient.patch(`/ayahs/${verseKey}/`, {
        translation_text: translationText,
        notes,
      })
      setAyah(res.data)
      setTranslationText(res.data.translation_text)
      setNotes(res.data.notes)
      setJustSaved(true)
    } catch {
      setError('সংরক্ষণ ব্যর্থ হয়েছে, আবার চেষ্টা করুন।')
    } finally {
      setSaving(false)
    }
  }

  async function handleFinalize() {
    setFinalizing(true)
    setError(null)
    try {
      const res = await apiClient.patch(`/ayahs/${verseKey}/`, { status: 'final' })
      setAyah(res.data)
    } catch (err) {
      setError(err.response?.data?.status?.[0] || 'আয়াত Final করা যায়নি।')
    } finally {
      setFinalizing(false)
    }
  }

  if (loading || !ayah) {
    return (
      <AppShell
        title={
          <span className="inline-flex items-center gap-3">
            <Link
              to={backTo}
              state={backState}
              className="text-muted-2 hover:text-heading"
              aria-label="সূরার আয়াত তালিকায় ফিরে যান"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            অনুবাদ ওয়ার্কস্পেস
          </span>
        }
      >
        <div className="p-8">
          <p className="text-muted">লোড হচ্ছে...</p>
        </div>
      </AppShell>
    )
  }

  const unassignedCount = ayah.word_occurrences.filter((o) => !o.meaning_text).length
  const assignedCount = ayah.word_occurrences.length - unassignedCount
  const isFinal = ayah.status === 'final'
  const canFinalize = !isFinal && !isDirty && translationText.trim().length > 0 && unassignedCount === 0
  const selectedOccurrence = ayah.word_occurrences.find((o) => o.id === selectedOccurrenceId) || null

  function handleWordSaved(updatedOccurrence) {
    setAyah((prev) => ({
      ...prev,
      word_occurrences: prev.word_occurrences.map((o) =>
        o.id === updatedOccurrence.id ? { ...o, ...updatedOccurrence } : o,
      ),
    }))
    setSelectedOccurrenceId(null)
  }

  return (
    <AppShell
      title={
        <span className="inline-flex items-center gap-3">
          <Link
            to={backTo}
            state={backState}
            className="text-muted-2 hover:text-heading"
            aria-label="সূরার আয়াত তালিকায় ফিরে যান"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          অনুবাদ ওয়ার্কস্পেস
        </span>
      }
      actions={
        <>
          <Badge variant={isFinal ? 'success' : 'warning'}>{isFinal ? 'Final' : 'Draft'}</Badge>
          {!isFinal && (
            <Button
              variant="success"
              onClick={handleFinalize}
              disabled={!canFinalize || finalizing}
              title={
                isDirty
                  ? 'আগে সংরক্ষণ করুন'
                  : !canFinalize
                    ? 'পূর্ণ অনুবাদ ও সব শব্দের অর্থ ছাড়া Final করা যাবে না'
                    : undefined
              }
            >
              {finalizing ? 'Final হচ্ছে...' : 'Final করুন'}
            </Button>
          )}
        </>
      }
    >
      <div className="flex flex-col gap-4 p-4 xl:gap-5 xl:p-6">
        {error && (
          <p className="rounded-lg bg-status-warning-bg px-4 py-2.5 text-[14.667px] text-status-warning-text">
            {error}
          </p>
        )}

        <div className="flex flex-col overflow-hidden rounded-2xl border border-header-line bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b-[1.333px] border-header-line bg-surface-subtle px-6 py-3 xl:py-4">
            <span className="text-[16.667px] font-semibold text-heading">
              {surah?.name_bangla} · আয়াত {toBanglaNumeral(ayah.ayah_number)}
            </span>
            <StatusLegend assignedCount={assignedCount} unassignedCount={unassignedCount} />
          </div>

          <div
            dir="rtl"
            className="flex flex-wrap content-start justify-start gap-x-8 gap-y-5 overflow-y-auto px-8 py-6"
            style={{ maxHeight: 'clamp(160px, 40vh, 440px)' }}
          >
            {ayah.word_occurrences.map((occurrence) => (
              <WordGridItem
                key={occurrence.id}
                occurrence={occurrence}
                selected={occurrence.id === selectedOccurrenceId}
                onClick={() => setSelectedOccurrenceId(occurrence.id)}
              />
            ))}
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-header-line bg-white">
          <div className="p-5 xl:p-[29.33px]">
            <div className="mb-3 flex items-center justify-between gap-4">
              <span className="text-[17.333px] font-semibold text-heading">আয়াতের পূর্ণ অনুবাদ</span>
              {justSaved && !isDirty && (
                <span className="flex items-center gap-1.5 text-[14.667px] font-medium text-link">
                  <CheckCircle2 className="h-[17.333px] w-[17.333px]" />
                  সংরক্ষিত হয়েছে
                </span>
              )}
            </div>
            <textarea
              ref={translationRef}
              rows={1}
              value={translationText}
              onChange={(e) => {
                setTranslationText(e.target.value)
                setJustSaved(false)
              }}
              style={{ minHeight: '56px', maxHeight: 'clamp(140px, 26vh, 256px)' }}
              className="w-full resize-none overflow-y-auto break-words rounded-[10.667px] border-[1.333px] border-border-subtle p-4 text-[18px] text-heading leading-[31.507px] transition-[height] duration-100 focus:outline-none focus:ring-2 focus:ring-brand-dark/20"
            />

            <div className="mb-3 mt-6 flex items-center justify-between gap-4">
              <span className="text-[17.333px] font-semibold text-heading">আয়াত সম্পর্কিত নোট</span>
              <span className="text-[14.667px] text-muted-2">আরবি, বাংলা বা ইংরেজি — যেকোনো ভাষায়</span>
            </div>
            <textarea
              ref={notesRef}
              rows={1}
              value={notes}
              onChange={(e) => {
                setNotes(e.target.value)
                setJustSaved(false)
              }}
              placeholder="এই আয়াত সম্পর্কে কোনো মন্তব্য থাকলে লিখুন…"
              style={{ minHeight: '56px', maxHeight: 'clamp(72px, 14vh, 128px)' }}
              className="w-full resize-none overflow-y-auto break-words rounded-[10.667px] border-[1.333px] border-border-subtle p-4 text-[17.333px] text-input-text placeholder:text-input-text transition-[height] duration-100 focus:outline-none focus:ring-2 focus:ring-brand-dark/20"
            />
          </div>

          <div className="flex items-center justify-end border-t-[1.333px] border-header-line px-[29.33px] py-5">
            <Button onClick={handleSave} disabled={saving || !isDirty}>
              {saving ? 'সংরক্ষণ হচ্ছে...' : 'সংরক্ষণ করুন'}
            </Button>
          </div>
        </div>
      </div>

      <WordAnalysisModal
        occurrence={selectedOccurrence}
        open={selectedOccurrence !== null}
        onClose={() => setSelectedOccurrenceId(null)}
        onSaved={handleWordSaved}
      />
    </AppShell>
  )
}
