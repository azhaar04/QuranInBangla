import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, BookText, CheckCircle2, Languages } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import Card from '../components/ui/Card'
import ProgressBar from '../components/ui/ProgressBar'
import Pagination from '../components/ui/Pagination'
import Tabs from '../components/ui/Tabs'
import apiClient from '../api/client'
import { toBanglaNumeral } from '../utils/numerals'
import { formatRelativeTime } from '../utils/datetime'

const ACTIVITY_PAGE_SIZE = 10

const RANGE_OPTIONS = [
  { key: '7d', label: '৭ দিন' },
  { key: '1m', label: '১ মাস' },
  { key: '6m', label: '৬ মাস' },
  { key: '1y', label: '১ বছর' },
]

function StatCard({ icon: Icon, value, total, caption }) {
  return (
    <Card className="flex h-[129.333px] items-center gap-4 px-6">
      <span className="flex h-[58.667px] w-[58.667px] shrink-0 items-center justify-center rounded-[13.333px] bg-alert-bg">
        <Icon className="h-6 w-6 text-link" />
      </span>
      <div className="min-w-0">
        <p className="flex items-baseline gap-1 whitespace-nowrap">
          <span className="text-[32px] font-bold tracking-[-0.6667px] text-heading">{value}</span>
          <span className="text-[20px] font-medium text-muted-2">/{total}</span>
        </p>
        <p className="truncate text-[16px] text-muted">{caption}</p>
      </div>
    </Card>
  )
}

function ProgressCard({ title, subtitle, bigValue, detail, progressValue, fillClassName }) {
  return (
    <Card className="flex h-[246.667px] flex-col justify-between p-6">
      <div>
        <h3 className="text-[18px] font-semibold text-heading">{title}</h3>
        <p className="text-[15.333px] text-muted">{subtitle}</p>
      </div>
      <div>
        <p className="text-[45.333px] font-bold text-brand-dark">{bigValue}</p>
        <p className="mb-3 text-[17.333px] text-muted">{detail}</p>
        <ProgressBar
          value={progressValue}
          heightClassName="h-[14.667px]"
          trackClassName="bg-progress-track"
          fillClassName={fillClassName}
        />
      </div>
    </Card>
  )
}

function ActivityIcon({ actionType }) {
  const isTranslation = actionType === 'ayah_translated' || actionType === 'ayah_updated'
  const Icon = isTranslation ? Languages : BookText
  return (
    <span
      className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-[13.333px] ${
        isTranslation ? 'bg-alert-bg text-link' : 'bg-search-highlight text-gold'
      }`}
    >
      <Icon className="h-[21.333px] w-[21.333px]" />
    </span>
  )
}

function ActivityText({ item }) {
  const ayahRef = `${item.surah_name_bangla ?? ''} ${toBanglaNumeral(item.verse_key ?? '')}`.trim()
  const wordSpan = (
    <span dir="rtl" className="font-arabic">
      «{item.word_arabic_text}»
    </span>
  )

  const isAyah = item.action_type === 'ayah_translated' || item.action_type === 'ayah_updated'
  const isFirstTime = item.action_type === 'ayah_translated' || item.action_type === 'word_meaning_added'

  const parts = []
  if (item.content_changed) parts.push(isFirstTime ? 'ইনপুট দেওয়া হয়েছে' : 'আপডেট করা হয়েছে')
  if (item.finalized) parts.push('ফাইনাল করা হয়েছে')
  const verbPhrase = parts.join(' ও ')

  if (isAyah) {
    return <>{ayahRef} আয়াতের তথ্য {verbPhrase}</>
  }
  return <>{wordSpan} শব্দের তথ্য {verbPhrase}</>
}

function ActivityRow({ item, isLast }) {
  const rowClass = `flex items-center gap-4 px-6 py-5 ${isLast ? '' : 'border-b-[1.333px] border-divider'}`
  const content = (
    <>
      <ActivityIcon actionType={item.action_type} />
      <span className="min-w-0 flex-1 truncate text-[17.333px] leading-[25.133px] text-heading">
        <ActivityText item={item} />
      </span>
      <span className="shrink-0 text-[14.667px] text-muted-2">{formatRelativeTime(item.created_at)}</span>
    </>
  )

  if (item.surah_number && item.ayah_number) {
    const isWordActivity = item.action_type === 'word_meaning_added' || item.action_type === 'word_meaning_updated'
    return (
      <Link
        to={`/surahs/${item.surah_number}/ayahs/${item.ayah_number}`}
        state={isWordActivity && item.word_occurrence_id ? { openOccurrenceId: item.word_occurrence_id } : undefined}
        className={`${rowClass} transition-colors hover:bg-page`}
      >
        {content}
      </Link>
    )
  }
  return <div className={rowClass}>{content}</div>
}

export default function DashboardPage() {
  const [summary, setSummary] = useState(null)
  const [activities, setActivities] = useState([])
  const [activityCount, setActivityCount] = useState(0)
  const [activityLoading, setActivityLoading] = useState(true)
  const [range, setRange] = useState(null)
  const [page, setPage] = useState(1)

  useEffect(() => {
    apiClient.get('/dashboard/summary/').then((res) => setSummary(res.data))
  }, [])

  useEffect(() => {
    setPage(1)
  }, [range])

  useEffect(() => {
    setActivityLoading(true)
    const params = { page, page_size: ACTIVITY_PAGE_SIZE }
    if (range) params.range = range
    apiClient
      .get('/dashboard/activity/', { params })
      .then((res) => {
        setActivities(res.data.results)
        setActivityCount(res.data.count)
      })
      .finally(() => setActivityLoading(false))
  }, [page, range])

  const totalPages = Math.max(1, Math.ceil(activityCount / ACTIVITY_PAGE_SIZE))

  return (
    <AppShell title="অগ্রগতি ড্যাশবোর্ড">
      <div className="flex flex-col gap-6 p-8">
        {!summary ? (
          <p className="text-muted">লোড হচ্ছে...</p>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-6">
              <StatCard
                icon={BookOpen}
                value={toBanglaNumeral(summary.surahs_started)}
                total={toBanglaNumeral(summary.surahs_total)}
                caption="সূরা শুরু হয়েছে"
              />
              <StatCard
                icon={CheckCircle2}
                value={toBanglaNumeral(summary.ayahs_final)}
                total={`${toBanglaNumeral(summary.ayahs_total)} আয়াত`}
                caption="আয়াত অনুবাদ অগ্রগতি (Final)"
              />
            </div>

            <div className="grid grid-cols-2 gap-6">
              <ProgressCard
                title="শব্দ অর্থ অগ্রগতি"
                subtitle="Word Meaning Progress"
                bigValue={`${toBanglaNumeral(
                  summary.word_meaning_total
                    ? Math.round((summary.word_meaning_final / summary.word_meaning_total) * 100)
                    : 0,
                )}%`}
                detail={`${toBanglaNumeral(summary.word_meaning_final)} / ${toBanglaNumeral(
                  summary.word_meaning_total,
                )} ইউনিক শব্দ Final`}
                progressValue={
                  summary.word_meaning_total ? (summary.word_meaning_final / summary.word_meaning_total) * 100 : 0
                }
                fillClassName="bg-gold"
              />
              <ProgressCard
                title="আয়াতভিত্তিক শব্দ ইনপুট অগ্রগতি"
                subtitle="Per-Ayah Word Entry Progress"
                bigValue={`${toBanglaNumeral(
                  summary.per_ayah_word_total
                    ? Math.round((summary.per_ayah_word_final / summary.per_ayah_word_total) * 100)
                    : 0,
                )}%`}
                detail={`${toBanglaNumeral(summary.per_ayah_word_final)} / ${toBanglaNumeral(
                  summary.per_ayah_word_total,
                )} আয়াতে সব শব্দ ইনপুট সম্পন্ন`}
                progressValue={
                  summary.per_ayah_word_total
                    ? (summary.per_ayah_word_final / summary.per_ayah_word_total) * 100
                    : 0
                }
                fillClassName="bg-[linear-gradient(to_right,var(--color-link),var(--color-progress-fill))]"
              />
            </div>
          </>
        )}

        <Card className="flex flex-col">
          <div className="flex flex-wrap items-center justify-between gap-4 p-6">
            <div>
              <h2 className="text-[19.333px] font-semibold text-heading">সাম্প্রতিক কার্যক্রম</h2>
              <p className="text-[15.333px] text-muted">Recent Activity</p>
            </div>
            <Tabs
              items={RANGE_OPTIONS}
              active={range}
              onChange={(key) => setRange(key === range ? null : key)}
            />
          </div>

          {activityLoading && activities.length === 0 ? (
            <p className="px-6 pb-6 text-muted">লোড হচ্ছে...</p>
          ) : activities.length === 0 ? (
            <p className="px-6 pb-6 text-muted">কোনো কার্যক্রম পাওয়া যায়নি।</p>
          ) : (
            <div className="max-h-[500px] overflow-y-auto border-t-[1.333px] border-divider">
              {activities.map((item, index) => (
                <ActivityRow key={item.id} item={item} isLast={index === activities.length - 1} />
              ))}
            </div>
          )}

          {totalPages > 1 && (
            <div className="border-t-[1.333px] border-header-line p-6">
              <Pagination page={page} totalPages={totalPages} onChange={setPage} variant="numbered" />
            </div>
          )}
        </Card>
      </div>
    </AppShell>
  )
}
