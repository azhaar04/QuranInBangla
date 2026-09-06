import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import Pagination from '../components/ui/Pagination'
import apiClient from '../api/client'
import { toBanglaNumeral } from '../utils/numerals'

const PAGE_SIZE = 15
const CELL_CLASS = 'flex min-w-0 items-center px-6 py-5'
const GRID_COLS = 'grid-cols-[minmax(160px,1fr)_minmax(320px,3fr)]'

function ResultRow({ result, isLast, onClick }) {
  const cellClass = `${CELL_CLASS} ${isLast ? '' : 'border-b-[1.333px] border-divider'} group-hover:bg-page transition-colors`
  return (
    <button type="button" onClick={onClick} className="group contents text-left cursor-pointer">
      <div className={cellClass}>
        <div>
          <p className="text-[16.667px] font-medium text-heading">
            {toBanglaNumeral(result.surah_number)} · {result.surah_name_bangla}
          </p>
          <p className="text-[15.333px] text-muted-2">আয়াত {toBanglaNumeral(result.ayah_number)}</p>
        </div>
      </div>
      <div className={`${cellClass} justify-end`}>
        <p dir="rtl" className="font-arabic text-[25.333px] leading-loose text-heading">
          {!result.is_full_ayah && '… '}
          {result.portion.map((token, index) => (
            <span key={index}>
              <span className={token.is_match ? 'rounded px-1 bg-search-highlight' : ''}>{token.text}</span>
              {index < result.portion.length - 1 ? ' ' : ''}
            </span>
          ))}
          {!result.is_full_ayah && ' …'}
        </p>
      </div>
    </button>
  )
}

export default function SearchPage() {
  const navigate = useNavigate()
  const [queryInput, setQueryInput] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [results, setResults] = useState([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  useEffect(() => {
    const timeout = setTimeout(() => setQuery(queryInput.trim()), 300)
    return () => clearTimeout(timeout)
  }, [queryInput])

  useEffect(() => {
    setPage(1)
  }, [query])

  useEffect(() => {
    if (!query) {
      setResults([])
      setTotalCount(0)
      setHasSearched(false)
      return
    }
    setLoading(true)
    setHasSearched(true)
    apiClient
      .get('/search/', { params: { q: query, page, page_size: PAGE_SIZE } })
      .then((res) => {
        setResults(res.data.results)
        setTotalCount(res.data.count)
      })
      .finally(() => setLoading(false))
  }, [query, page])

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE))

  return (
    <AppShell title="অনুসন্ধান">
      <div className="p-8">
        <div className="rounded-2xl border border-header-line bg-white p-6">
          <label className="text-[16px] font-medium text-label">
            আরবি শব্দ লিখুন (ডায়াক্রিটিক্স ছাড়াই লেখা যাবে)
          </label>
          <div className="relative mt-3">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-2" />
            <input
              type="text"
              dir="rtl"
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              placeholder="যেমন: رحيم"
              className="h-[66.667px] w-full rounded-xl border border-border-subtle bg-surface-subtle pl-4 pr-14 font-arabic text-[26.667px] text-heading placeholder:text-muted-2 focus:border-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-dark"
            />
          </div>
          {hasSearched && !loading && (
            <p className="mt-3 text-[16px] text-muted-2">
              {totalCount > 0
                ? `${toBanglaNumeral(totalCount)}টি আয়াতে "${query}" শব্দটি পাওয়া গেছে`
                : `"${query}" শব্দটি কোনো আয়াতে পাওয়া যায়নি`}
            </p>
          )}
        </div>

        {hasSearched && (
          <div className="mt-6">
            {loading ? (
              <p className="text-muted">লোড হচ্ছে...</p>
            ) : results.length === 0 ? (
              <p className="text-muted">কোনো ফলাফল পাওয়া যায়নি।</p>
            ) : (
              <>
                <div className="overflow-hidden rounded-2xl border border-header-line bg-white">
                  <div className={`grid ${GRID_COLS}`}>
                    <div className="border-b-[1.333px] border-header-line bg-surface-subtle px-6 py-4 text-[14.667px] font-semibold text-muted">
                      সূরা · আয়াত
                    </div>
                    <div className="border-b-[1.333px] border-header-line bg-surface-subtle px-6 py-4 text-right text-[14.667px] font-semibold text-muted">
                      আরবি টেক্সট
                    </div>

                    {results.map((result, index) => (
                      <ResultRow
                        key={result.verse_key}
                        result={result}
                        isLast={index === results.length - 1}
                        onClick={() =>
                          navigate(`/surahs/${result.surah_number}/ayahs/${result.ayah_number}`)
                        }
                      />
                    ))}
                  </div>
                </div>
                <Pagination page={page} totalPages={totalPages} onChange={setPage} className="mt-5" />
              </>
            )}
          </div>
        )}
      </div>
    </AppShell>
  )
}
