const BANGLA_DIGITS = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯']

export function toBanglaNumeral(value) {
  return String(value).replace(/[0-9]/g, (digit) => BANGLA_DIGITS[Number(digit)])
}
