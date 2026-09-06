import { toBanglaNumeral } from './numerals'

const BANGLA_MONTHS = [
  'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন',
  'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর',
]

export function formatRelativeTime(isoString) {
  const date = new Date(isoString)
  const diffMinutes = Math.floor((Date.now() - date.getTime()) / 60000)

  if (diffMinutes < 1) return 'এইমাত্র'
  if (diffMinutes < 60) return `${toBanglaNumeral(diffMinutes)} মিনিট আগে`

  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${toBanglaNumeral(diffHours)} ঘণ্টা আগে`

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${toBanglaNumeral(diffDays)} দিন আগে`

  return `${toBanglaNumeral(date.getDate())} ${BANGLA_MONTHS[date.getMonth()]}, ${toBanglaNumeral(date.getFullYear())}`
}
