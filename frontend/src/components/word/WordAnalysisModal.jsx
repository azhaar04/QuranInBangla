import { useEffect, useRef, useState } from 'react'
import Modal from '../ui/Modal'
import RemovableChipInput from '../ui/RemovableChipInput'
import apiClient from '../../api/client'
import { autoResizeTextarea } from '../../utils/textarea'

const EMPTY_NOTE = {
  root: '',
  meaning_basra: '',
  meaning_kufa: '',
  meaning_baghdad: '',
  pattern: '',
  note_for_pattern: '',
  grammatical_information: '',
  derived_forms: [],
  notes: '',
}

const INPUT_CLASS =
  'h-[50.667px] w-full rounded-[10.667px] border-[1.333px] border-border-subtle bg-white px-4 text-[16.667px] text-heading placeholder:text-input-text focus:outline-none focus:ring-2 focus:ring-brand-dark/20'

const ARABIC_INPUT_CLASS =
  'h-14 w-full rounded-[10.667px] border-[1.333px] border-border-subtle bg-white px-4 text-[28px] leading-[1.6] text-heading placeholder:text-input-text focus:outline-none focus:ring-2 focus:ring-brand-dark/20 font-arabic'

function Field({ label, children }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[15.333px] font-medium text-label">{label}</span>
      {children}
    </label>
  )
}

function AutoTextarea({ inputRef, value, onChange, placeholder, minHeight, maxHeight }) {
  return (
    <textarea
      ref={inputRef}
      rows={1}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      style={{ minHeight: `${minHeight}px`, maxHeight }}
      className="w-full resize-none overflow-y-auto break-words rounded-[10.667px] border-[1.333px] border-border-subtle bg-white p-4 text-[16.667px] text-heading placeholder:text-input-text transition-[height] duration-100 focus:outline-none focus:ring-2 focus:ring-brand-dark/20"
    />
  )
}

export default function WordAnalysisModal({ occurrence, open, onClose, onSaved }) {
  const [meaningText, setMeaningText] = useState('')
  const [note, setNote] = useState(EMPTY_NOTE)
  const [wordArabicText, setWordArabicText] = useState('')
  const [isMeaningFinal, setIsMeaningFinal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const basraRef = useRef(null)
  const kufaRef = useRef(null)
  const baghdadRef = useRef(null)
  const patternExplanationRef = useRef(null)
  const noteRef = useRef(null)

  useEffect(() => {
    if (!open || !occurrence) return
    setMeaningText(occurrence.meaning_text || '')
    setNote(EMPTY_NOTE)
    setWordArabicText(occurrence.word_arabic_text || '')
    setIsMeaningFinal(false)
    setError(null)
    setLoading(true)
    Promise.all([
      apiClient.get(`/words/${occurrence.word}/note/`),
      apiClient.get(`/words/${occurrence.word}/`),
    ])
      .then(([noteRes, wordRes]) => {
        setNote({ ...EMPTY_NOTE, ...noteRes.data })
        setWordArabicText(wordRes.data.arabic_text)
        setIsMeaningFinal(Boolean(wordRes.data.is_meaning_final))
      })
      .catch(() => setError('শব্দের তথ্য লোড করা যায়নি।'))
      .finally(() => setLoading(false))
  }, [open, occurrence])

  useEffect(() => {
    autoResizeTextarea(basraRef.current, note.meaning_basra, 50.667)
  }, [note.meaning_basra, loading])

  useEffect(() => {
    autoResizeTextarea(kufaRef.current, note.meaning_kufa, 50.667)
  }, [note.meaning_kufa, loading])

  useEffect(() => {
    autoResizeTextarea(baghdadRef.current, note.meaning_baghdad, 50.667)
  }, [note.meaning_baghdad, loading])

  useEffect(() => {
    autoResizeTextarea(patternExplanationRef.current, note.note_for_pattern, 50.667)
  }, [note.note_for_pattern, loading])

  useEffect(() => {
    autoResizeTextarea(noteRef.current, note.notes, 56)
  }, [note.notes, loading])

  if (!open || !occurrence) return null

  function updateNote(field, value) {
    setNote((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      const noteRequest = apiClient.patch(`/words/${occurrence.word}/note/`, {
        root: note.root,
        meaning_basra: note.meaning_basra,
        meaning_kufa: note.meaning_kufa,
        meaning_baghdad: note.meaning_baghdad,
        pattern: note.pattern,
        note_for_pattern: note.note_for_pattern,
        grammatical_information: note.grammatical_information,
        derived_forms: note.derived_forms,
        notes: note.notes,
      })

      const finalRequest = apiClient.patch(`/words/${occurrence.word}/`, {
        is_meaning_final: isMeaningFinal,
      })

      const trimmedMeaning = meaningText.trim()
      const meaningChanged = trimmedMeaning && trimmedMeaning !== (occurrence.meaning_text || '')
      const meaningRequest = meaningChanged
        ? apiClient.patch(`/word-occurrences/${occurrence.id}/meaning/`, {
            meaning_text: trimmedMeaning,
          })
        : null

      const [, , occurrenceRes] = await Promise.all([noteRequest, finalRequest, meaningRequest])

      onSaved({
        ...occurrence,
        meaning_text: occurrenceRes?.data.meaning_text ?? occurrence.meaning_text,
        meaning: occurrenceRes?.data.meaning ?? occurrence.meaning,
      })
    } catch {
      setError('সংরক্ষণ ব্যর্থ হয়েছে, আবার চেষ্টা করুন।')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} dismissible={false} className="max-w-[min(1400px,92vw)]">
      <div className="flex items-center gap-4 border-b-[1.333px] border-header-line px-8 py-5">
        <span className="font-arabic text-[37.333px] text-brand-dark">{wordArabicText}</span>
        <span className="text-[20px] font-semibold text-heading">
          নির্বাচিত শব্দ — ব্যাকরণগত বিশ্লেষণ
        </span>
      </div>

      <div className="flex flex-col gap-5 px-8 py-6">
        {error && (
          <p className="rounded-lg bg-status-warning-bg px-4 py-2.5 text-[14.667px] text-status-warning-text">
            {error}
          </p>
        )}

        <Field label="শব্দের বাংলা অনুবাদ">
          <input
            value={meaningText}
            onChange={(e) => setMeaningText(e.target.value)}
            className={INPUT_CLASS}
          />
        </Field>

        <Field label="রুট শব্দ / Root">
          <input
            value={note.root}
            onChange={(e) => updateNote('root', e.target.value)}
            dir="rtl"
            className={ARABIC_INPUT_CLASS}
          />
        </Field>

        <div className="grid grid-cols-3 gap-4">
          <Field label="বসরা">
            <AutoTextarea
              inputRef={basraRef}
              value={note.meaning_basra}
              onChange={(e) => updateNote('meaning_basra', e.target.value)}
              minHeight={50.667}
              maxHeight="clamp(50.667px, 16vh, 140px)"
            />
          </Field>
          <Field label="কুফা">
            <AutoTextarea
              inputRef={kufaRef}
              value={note.meaning_kufa}
              onChange={(e) => updateNote('meaning_kufa', e.target.value)}
              minHeight={50.667}
              maxHeight="clamp(50.667px, 16vh, 140px)"
            />
          </Field>
          <Field label="বাগদাদ">
            <AutoTextarea
              inputRef={baghdadRef}
              value={note.meaning_baghdad}
              onChange={(e) => updateNote('meaning_baghdad', e.target.value)}
              minHeight={50.667}
              maxHeight="clamp(50.667px, 16vh, 140px)"
            />
          </Field>
        </div>

        <Field label="Pattern">
          <input
            value={note.pattern}
            onChange={(e) => updateNote('pattern', e.target.value)}
            dir="rtl"
            className={ARABIC_INPUT_CLASS}
          />
        </Field>

        <Field label="Pattern এর ব্যাখ্যা">
          <AutoTextarea
            inputRef={patternExplanationRef}
            value={note.note_for_pattern}
            onChange={(e) => updateNote('note_for_pattern', e.target.value)}
            minHeight={50.667}
            maxHeight="clamp(50.667px, 16vh, 140px)"
          />
        </Field>

        <Field label="Grammatical Information">
          <input
            value={note.grammatical_information}
            onChange={(e) => updateNote('grammatical_information', e.target.value)}
            className={INPUT_CLASS}
          />
        </Field>

        <Field label="এই রুট থেকে উদ্ভূত শব্দ / Forms derived from this Root">
          <RemovableChipInput
            value={note.derived_forms}
            onChange={(next) => updateNote('derived_forms', next)}
          />
        </Field>

        <Field label="নোট / Note">
          <AutoTextarea
            inputRef={noteRef}
            value={note.notes}
            onChange={(e) => updateNote('notes', e.target.value)}
            placeholder="এই শব্দ সম্পর্কে অতিরিক্ত ব্যাখ্যা বা মন্তব্য লিখুন…"
            minHeight={56}
            maxHeight="clamp(72px, 20vh, 200px)"
          />
        </Field>

        <label className="flex items-center gap-3 rounded-[10.667px] border-[1.333px] border-border-subtle bg-white px-4 py-3.5">
          <input
            type="checkbox"
            checked={isMeaningFinal}
            onChange={(e) => setIsMeaningFinal(e.target.checked)}
            className="h-5 w-5 accent-brand-dark"
          />
          <span className="text-[16.667px] font-medium text-heading">
            চূড়ান্ত (Final) — এই শব্দের অর্থ ও তথ্য সম্পূর্ণ ও যাচাইকৃত
          </span>
        </label>
      </div>

      <div className="flex items-center justify-end gap-3 px-8 pb-8">
        <button
          type="button"
          onClick={onClose}
          disabled={saving}
          className="h-[50.667px] rounded-[10.667px] border-[1.333px] border-border-subtle bg-white px-5 text-[16.667px] font-medium text-label hover:bg-black/5 disabled:cursor-not-allowed disabled:opacity-60"
        >
          বাতিল
        </button>
        <button
          type="button"
          onClick={handleSave}
          disabled={saving || loading}
          className="h-[50.667px] rounded-[10.667px] bg-brand-dark px-5 text-[16.667px] font-medium text-white hover:bg-brand-dark/90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? 'সংরক্ষণ হচ্ছে...' : 'শব্দের তথ্য সংরক্ষণ করুন'}
        </button>
      </div>
    </Modal>
  )
}
