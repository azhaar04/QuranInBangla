import { Fragment, useEffect, useState } from 'react'
import { ArrowDown, ArrowUp, ChevronsUpDown } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import SearchInput from '../components/ui/SearchInput'
import Tabs from '../components/ui/Tabs'
import Badge from '../components/ui/Badge'
import Pagination from '../components/ui/Pagination'
import apiClient from '../api/client'
import { toBanglaNumeral } from '../utils/numerals'

const PAGE_SIZE = 50

const STATUS_FILTERS = [
  { key: 'all', label: 'সব' },
  { key: 'complete', label: 'সম্পূর্ণ' },
  { key: 'incomplete', label: 'অসম্পূর্ণ' },
]

const CELL_CLASS = 'flex min-w-0 items-center px-6 py-4'
const GRID_COLS =
  'grid-cols-[minmax(160px,3fr)_minmax(120px,2fr)_minmax(200px,4fr)_minmax(160px,3fr)_minmax(120px,2fr)_minmax(110px,2fr)]'

function formatOccurrence(count) {
  return `${toBanglaNumeral(count.toLocaleString('en-US'))} বার`
}

function WordRow({ word, isLast }) {
  const cellClass = `${CELL_CLASS} ${isLast ? '' : 'border-b-[1.333px] border-divider'}`
  return (
    <Fragment>
      <div className={cellClass}>
        <span className="font-arabic text-[24px] text-heading">{word.arabic_text}</span>
      </div>
      <div className={cellClass}>
        <span className="font-arabic text-[18px] text-muted-2">{word.root || '—'}</span>
      </div>
      <div className={cellClass}>
        <span className="truncate text-[16px] text-heading">{word.default_meaning || '—'}</span>
      </div>
      <div className={cellClass}>
        <span className="truncate text-[16px] text-label">{word.grammatical_information || '—'}</span>
      </div>
      <div className={cellClass}>
        <span className="text-[15.333px] text-label">{formatOccurrence(word.occurrence_count)}</span>
      </div>
      <div className={`${cellClass} justify-center`}>
        {word.is_meaning_final ? (
          <Badge variant="success">Final</Badge>
        ) : (
          <Badge variant="neutral">অসম্পূর্ণ</Badge>
        )}
      </div>
    </Fragment>
  )
}

function SortIcon({ direction }) {
  if (direction === 'asc') return <ArrowUp className="h-3.5 w-3.5" />
  if (direction === 'desc') return <ArrowDown className="h-3.5 w-3.5" />
  return <ChevronsUpDown className="h-3.5 w-3.5 opacity-50" />
}

function SortableHeader({ label, field, sortField, sortDir, onSort, className = '' }) {
  const direction = sortField === field ? sortDir : null
  return (
    <button
      type="button"
      onClick={() => onSort(field)}
      className={`flex items-center gap-1.5 text-left transition-colors hover:text-heading ${className}`}
    >
      {label}
      <SortIcon direction={direction} />
    </button>
  )
}

function WordTable({ words, sortField, sortDir, onSort }) {
  const headerClass =
    'border-b-[1.333px] border-header-line bg-surface-subtle-2 px-6 py-4 text-[14px] font-semibold tracking-[0.4px] text-muted-2 uppercase'
  return (
    <div className="overflow-hidden rounded-[13.333px] border border-header-line bg-white">
      <div className={`grid ${GRID_COLS}`}>
        <div className={headerClass}>
          <SortableHeader label="শব্দ" field="arabic_text" sortField={sortField} sortDir={sortDir} onSort={onSort} />
        </div>
        <div className={headerClass}>রুট</div>
        <div className={headerClass}>ডিফল্ট অর্থ</div>
        <div className={headerClass}>পার্টস অফ স্পিচ</div>
        <div className={headerClass}>
          <SortableHeader
            label="উপস্থিতি"
            field="occurrence_count"
            sortField={sortField}
            sortDir={sortDir}
            onSort={onSort}
          />
        </div>
        <div className={`${headerClass} text-center`}>অবস্থা</div>

        {words.map((word, index) => (
          <WordRow key={word.id} word={word} isLast={index === words.length - 1} />
        ))}
      </div>
    </div>
  )
}

export default function WordDictionaryPage() {
  const [words, setWords] = useState([])
  const [loading, setLoading] = useState(true)
  const [counts, setCounts] = useState({ all: 0, complete: 0, incomplete: 0 })
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [statusFilter, setStatusFilter] = useState('all')
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [sortField, setSortField] = useState('arabic_text')
  const [sortDir, setSortDir] = useState('asc')

  useEffect(() => {
    const timeout = setTimeout(() => setSearch(searchInput.trim()), 300)
    return () => clearTimeout(timeout)
  }, [searchInput])

  useEffect(() => {
    setPage(1)
  }, [statusFilter, search, sortField, sortDir])

  useEffect(() => {
    setLoading(true)
    const params = { page, page_size: PAGE_SIZE }
    if (search) params.search = search
    if (statusFilter !== 'all') params.is_meaning_final = statusFilter === 'complete'
    params.ordering = sortDir === 'desc' ? `-${sortField}` : sortField

    apiClient
      .get('/words/', { params })
      .then((res) => {
        setWords(res.data.results)
        setTotalCount(res.data.count)
        setCounts(res.data.counts)
      })
      .finally(() => setLoading(false))
  }, [page, statusFilter, search, sortField, sortDir])

  function handleSort(field) {
    if (sortField === field) {
      setSortDir((dir) => (dir === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortField(field)
      setSortDir('asc')
    }
  }

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE))

  return (
    <AppShell
      title="শব্দ অভিধান"
      subtitle="প্রতিটি ইউনিক শব্দের রুট, অর্থ ও ব্যাকরণগত তথ্য"
      actions={
        <SearchInput
          placeholder="রুট বা শব্দ খুঁজুন..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="w-[266.667px]"
        />
      }
    >
      <div className="flex items-center gap-3 border-b-[1.333px] border-header-line bg-white px-[37.33px] py-5">
        <Tabs
          items={STATUS_FILTERS.map((f) => ({ ...f, label: `${f.label} (${toBanglaNumeral(counts[f.key] ?? 0)})` }))}
          active={statusFilter}
          onChange={setStatusFilter}
        />
      </div>

      <div className="p-8">
        {loading ? (
          <p className="text-muted">লোড হচ্ছে...</p>
        ) : words.length === 0 ? (
          <p className="text-muted">কোনো শব্দ পাওয়া যায়নি।</p>
        ) : (
          <>
            <WordTable words={words} sortField={sortField} sortDir={sortDir} onSort={handleSort} />
            <Pagination page={page} totalPages={totalPages} onChange={setPage} className="mt-5" />
          </>
        )}
      </div>
    </AppShell>
  )
}
