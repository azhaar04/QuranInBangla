# QuranInBangla — Frontend Development Plan

6 ta mockup (Login, Dashboard, Surah List, Ayah View, Word Dictionary, Search)
dekhe analysis kora holo, ar sheta theke ekta **design-system-first** development
plan draft kora holo — jate button color-er moto jekono design token (color,
font, spacing, radius) **ekjaygay fixed thake, baki shob jaygay shudhu reference
kora hoy**. Eta shudhu button-e na, shob UI element-e apply hobe.

**Status: shob 6-ta page-er exact design data ekhon Figma MCP diye direct pull
kora — ar approximate/estimate value nei ei document-e.**

---

## ⚠️ Font decision (Claude Code, eta miss করো না)

**Bangla text — page-onujayi, mockup-e jei font ache shei-i use korte hobe
(apatoto, client-er latest instruction):**

- Login page → **Noto Sans Bengali** (already implemented, eta-i thakbe)
- Dashboard, Sidebar, Surah List, Ayah View, Word Dictionary, Search →
  **Hind Siliguri**
- English UI text jekhane ache (Login-er input placeholder, logo wordmark) →
  **Inter**

> Note: age (ei conversation-erই earlier part-e) Bangla UI font hishebe
> **Kalpurush** confirmed kora hoyechilo (Hind Siliguri-ke reject kore, karon
> shetake "India-market-oriented" mone hoyechilo). Client ekhon explicitly
> bolechen — Login page already Noto Sans Bengali diye build hoye geche,
> tai **apatoto** shob page-e jekhane jei font mockup-e ache shei-i use
> korte, ek-font-shob-jaygay approach-er bodole. Eta ekta **temporary/
> pragmatic decision** — Kalpurush-e switch kora future-e revisit hote pare,
> kintu ekhon-er jonno **per-page mockup font-i final.**

**Arabic text — eta change hoyni, age-r decision unchanged:**

- Arabic text (word grid, root letters, search input, Ayah/Surah Arabic
  preview) → mockup-e **Amiri** ache **সব page-e**, kintu project-er
  confirmed decision (client 2-bar reconfirm korechen) holo **QPC Hafs**
  use kora, Amiri na. Ei ekta jaygay-e shudhu Figma-r literal font-name
  **override** korte hobe — baki shob jaygay (Bangla) mockup-er font-i
  follow korte hobe.

Ei document-e niche code snippet-e `font-['Amiri:...']` dekha gele
implementation-e QPC Hafs bodle nite hobe. `font-['Hind_Siliguri:...']` ba
`font-['Noto_Sans_Bengali:...']` dekha gele **shegula ইতিমধ্যে সঠিক** — oi
font-i use korte hobe, bodlanor dorkar nei.

---

## 1. Mockup theke ja ja pattern paওয়া gelo

### Color tokens — master list (shob ✅ CONFIRMED, Figma MCP diye direct pull)

| Token name | Hex / value | Kothay use hoyeche |
|---|---|---|
| `primary` (deep forest green) | `#063d2c` | Sidebar bg, Login card header bg, active pagination/pill, avatar text, ayah-number badge bg, primary buttons |
| `accent` (gold) | `#c9a227` | Logo "Quran"/"Bangla" text, avatar circle bg, active nav indicator, progress fill (word meaning), ayah-number badge text |
| `action-green` (jewel green) | `#0f6e56` | Ayah View Prev/Next buttons, Login "পাসওয়ার্ড ভুলে গেছেন?" link, progress-bar gradient start |
| `background` (main content area) | `#f4f2ee` | Content bg (all authenticated pages), inactive pill bg, Word Dictionary top-right search-input bg |
| `surface` (card/page bg) | `#ffffff` | Card, header bar, page container bg |
| `surface-subtle` (off-white panel) | `#f7f5ef` | Search Arabic-input bg, Search/Word Dictionary table header row bg |
| `surface-subtle-2` (off-white panel, Surah List variant) | `#faf9f5` | Surah List table header row bg — **note: Figma has 2 near-identical off-white tones (`#f7f5ef` vs `#faf9f5`); kept separate as extracted, do not silently merge** |
| `card-bg-alt` (Login card) | `#fafaf8` | Login card background |
| `border` (card border) | `#ece8df` | Card border, header border-bottom |
| `border-subtle` | `#e0ddd6` | Table/search-input border (Surah List, Search, Word Dictionary), filter-pill border |
| `border-input` (Login) | `#d4d0c8` | Login username/password input border |
| `row-divider` | `#f4f1ea` | Row border in Search/Word Dictionary tables |
| `row-divider-2` | `#f1eee7` | Row divider in Dashboard Recent Activity |
| `progress-track` | `#eeebe4` | Dashboard progress-card bar track |
| `progress-track-2` (Surah List row bar) | `#f0ede6` | Surah List per-row progress bar track — near-duplicate of `progress-track`, kept separate as extracted |
| `progress-fill-gradient` | `#0f6e56 → #1d9e75` | Ayah word-entry progress bar (green gradient) |
| `avatar-neutral-bg` | `#f1efe8` | Surah List ruku-number circle bg; Word Dictionary "অসম্পূর্ণ" (neutral) status badge bg |
| `text-heading` (dark) | `#221f1a` | Page title, stat numbers, activity text, table cell primary text |
| `text-muted` | `#8a867c` | Card subtitle/caption text, table header label text |
| `text-muted-2` (lighter) | `#a09c94` | "/total" suffix, timestamp, table secondary text, placeholder text |
| `text-input` (Login) | `#757575` | Login input entered-text/placeholder color |
| `text-pagination-inactive` | `#5a5750` | Inactive pagination/pill text, table secondary column text |
| `icon-bg-green` (soft) | `#eff9f5` | Stat-card icon bg, "translation" activity icon bg, Login notice-box bg |
| `icon-bg-gold` / **search-match-highlight** (soft) | `#fbf3d9` | "word meaning" activity icon bg — **same token reused for Search page's matched-Arabic-word highlight** |
| `notice-border` (Login) | `#b8e0d2` | Login notice/info box border |
| `notice-text` (Login) | `#0b5a45` | Login notice/info box text |
| `divider` | `#f1eee7` | Horizontal divider between activity rows |
| `sidebar-border` | `rgba(255,255,255,0.08)` | Sidebar section borders (top/bottom) |
| `sidebar-text-inactive` | `rgba(255,255,255,0.55)` | Inactive nav item text |
| `sidebar-text-label` | `rgba(255,255,255,0.32)` | "প্রধান মেনু"/"টুলস" section labels |
| `sidebar-active-bg` | `rgba(255,255,255,0.1)` | Active nav item background |
| `logo-badge-bg` | `rgba(201,162,39,0.14)` | Logo container bg (sidebar) |
| `logo-badge-border` | `rgba(201,162,39,0.4)` | Logo container border (sidebar) |
| `login-pill-bg` | `rgba(201,162,39,0.06)` | Login "Translation Management System" pill bg — slightly different alpha than sidebar logo badge |
| `login-pill-border` | `rgba(201,162,39,0.55)` | Login pill border |
| `card-shadow` | `0px 26.667px 80px 0px rgba(0,0,0,0.15)` | Page-level card shadow (Dashboard, Search, Word Dictionary, Ayah View) |
| `login-card-shadow` | `0px 40px 106.667px 0px rgba(0,0,0,0.35)` | Login card shadow (stronger — floats over dark bg) |
| **Status: Final/সম্পন্ন** (success) | bg `#e1f5ee` / text `#085041` | Status badge — Surah List, Ayah View, Word Dictionary |
| **Status: চলমান/Draft/খসড়া** (warning) | bg `#faeeda` / text `#633806` | Status badge |
| **Status: বাকি/অসম্পূর্ণ** (neutral) | bg `#f1efe8` / text `#5a5750` | Status badge |
| **Search-match highlight** | bg `#fbf3d9` (= `icon-bg-gold`) | Search result-e matched Arabic word background |

### Typography

- Bangla UI + body text → **page-onujayi, mockup follow kore** (apatoto):
  Login-e **Noto Sans Bengali**, baki shob page-e (Dashboard, Sidebar,
  Surah List, Ayah View, Word Dictionary, Search) **Hind Siliguri** — dekho
  ⚠️ box, upore
- Arabic text → **QPC Hafs** (final decision, unchanged — Figma mockup
  "Amiri" use kore shob jaygay: word-by-word grid, root letters, surah-name
  Arabic, search input/results — shob jaygay QPC Hafs-e switch korte hobe)
- Numbers already Bangla numeral (১, ২, ৩...) — consistent shob jaygay

---

## 1.5 Exact Layout Specs — CONFIRMED (shob 6 page)

Figma MCP diye direct pull kora — height/width/spacing/radius/font-size shob
exact px value. Font-family column-e neeche jekhane "(Figma: Amiri)" note
dekha jabe, shekhane implementation-e **QPC Hafs** use korte hobe (Arabic-er
jonno confirmed override — dekho ⚠️ box, upore). Bangla font (Hind Siliguri
/ Noto Sans Bengali) already page-onujayi mockup-er shathe match kore —
oigulote kono override lagbe na.

### Sidebar (`Aside`) — width `293.333px`, full height, bg `#063d2c`

| Element | Spec |
|---|---|
| Top border (logo row bottom) | `1.333px solid rgba(255,255,255,0.08)`, row height ~98.67px |
| Logo badge | `50.667px` square, radius `12px`, left `24px`, bg `rgba(201,162,39,0.14)`, border `1.333px rgba(201,162,39,0.4)` |
| Logo icon | `26×24px`, centered inside badge |
| Brand text "Quran in Bangla" | left `90.67px`, font `17.333px` SemiBold — "Quran"/"Bangla" in `#c9a227`, "in" in white |
| Section label ("প্রধান মেনু"/"টুলস") | font `13.333px` SemiBold, letter-spacing `1.0667px`, uppercase, color `rgba(255,255,255,0.32)` |
| Nav item (each) | height `56px`, icon `21.333px` at left `14.67px`, text left `50.67px` font `17.333px` |
| Nav item — inactive | text Medium weight, color `rgba(255,255,255,0.55)` |
| Nav item — active | bg `rgba(255,255,255,0.1)`, radius `10.667px`, text SemiBold white, right-edge accent bar width `2.667px` radius `2.667px` bg `#c9a227` |
| Footer (user block) top border | `1.333px solid rgba(255,255,255,0.08)`, starts at y `1112px` (in 1200px-tall frame) |
| Avatar circle | size `45.333px`, radius `22.667px` (full circle), bg `#c9a227`, initial letter centered, color `#063d2c`, font `17.333px` Bold |
| User name | left `77.33px`, font `16.667px` Medium, white |
| Role label ("Admin") | left `77.33px`, top `56.67px`, font `14px` Regular, color `#c9a227` |
| Logout icon | right-aligned, size `21.333px` |

**Confirmed identical across all 5 authenticated pages** (Dashboard, Surah
List, Ayah View, Word Dictionary, Search) — build once, reuse everywhere,
only the active nav item changes.

### Dashboard Page — `1920×1200px`, radius `18.667px`, shadow `0px 26.667px 80px rgba(0,0,0,0.15)`

| Element | Spec |
|---|---|
| Header bar | height `82.67px`, bg white, border-bottom `1.333px #ece8df`, title left `37.33px` font `22.667px` Medium color `#221f1a` |
| Content bg | `#f4f2ee`, starts top `82.67px`, left `293.33px` (after sidebar) |
| **Stat card** (×2) | height `129.333px`, radius `16px`, border `1.333px #ece8df`, bg white |
| — icon box | `58.667px` square, radius `13.333px`, bg `#eff9f5` |
| — big number | font `32px` Bold, color `#221f1a`, tracking `-0.6667px` |
| — "/total" suffix | font `20px` Medium, color `#a09c94` |
| — caption label | font `16px` Regular, color `#8a867c` |
| **Progress card** (×2) | height `246.667px`, radius `18.667px`, border `1.333px #ece8df`, bg white |
| — title | font `18px` SemiBold, color `#221f1a` |
| — subtitle (English) | font `15.333px` Regular, color `#8a867c` |
| — big percentage/number | font `45.333px` Bold, color `#063d2c` |
| — detail text | font `17.333px` Regular, color `#8a867c` |
| — progress bar | height `14.667px`, radius `26.667px`, track bg `#eeebe4`; fill = solid `#c9a227` (word meaning) or gradient `#0f6e56→#1d9e75` (ayah entry) |
| **Recent Activity card** | height `638.667px`, radius `18.667px`, border `1.333px #ece8df`, bg white |
| — title | font `19.333px` SemiBold, color `#221f1a` |
| — subtitle (English) | font `15.333px` Regular, color `#8a867c` |
| — time-range pill (active) | height `41.333px`, radius `26.667px`, bg `#063d2c`, text white `15.333px` SemiBold |
| — time-range pill (inactive) | bg `#f4f2ee`, border `1.333px #ece8df`, text `#5a5750` `15.333px` Medium |
| — activity row icon box | `48px` height, radius `13.333px`, icon `21.333px`; bg `#eff9f5` (translation) or `#fbf3d9` (word meaning) |
| — activity row text | font `17.333px` Regular, color `#221f1a`, line-height `25.133px` |
| — activity row timestamp | font `14.667px` Regular, color `#a09c94` |
| — row divider | height `1.333px`, bg `#f1eee7` |
| — row vertical spacing | ~`84px` between rows |
| — pagination button | `37.333px` square, radius `9.333px`; active bg `#063d2c` text white; inactive bg `#f4f2ee` border `1.333px #ece8df` text `#5a5750`, font `16px` |

### Login Page — full-screen `#063d2c` bg + centered card `586.667×944.52px`

| Element | Spec |
|---|---|
| Page background | `#063d2c`, subtle radial gold gradient overlay (`rgba(201,162,39,0.1)` → transparent, opacity ~0.07-0.1) — decorative only, low priority |
| Card | `586.667×944.52px`, centered, bg `#fafaf8`, radius `16px`, shadow `0px 40px 106.667px rgba(0,0,0,0.35)` |
| Card header block | height `300px`, bg `#063d2c`, border `2px solid #fafaf8`, top corners radius `16px` |
| — Logo icon | `~80px` tall icon area, centered, top of header |
| — Brand text "Quran in Bangla" | font `26.667px` Medium (Figma: Inter) — "Quran"/"Bangla" gold `#c9a227`, "in" white |
| — Pill "Translation Management System" | height `36px`, bg `rgba(201,162,39,0.06)`, border `1.333px rgba(201,162,39,0.55)`, radius pill (full), text `14px` Medium color `#c9a227`, tracking `0.6667px` |
| Heading "স্বাগতম" | font `28px` Medium (Figma: Noto Sans Bengali), color `#221f1a` |
| Subtitle "আপনার অ্যাকাউন্টে প্রবেশ করুন" | font `17.333px` Regular, color `#8a867c` |
| Field label ("ইউজারনেম" / "পাসওয়ার্ড") | font `16.667px` Medium (Figma: Noto Sans Bengali), color `#5a5750` |
| Text input | height `56px`, bg white, border `1.333px #d4d0c8`, radius `10.667px`; entered text `18px` Regular (Figma: Inter) color `#757575`; left icon `21.333px` |
| Password input | same as text input; right-side show/hide eye icon `~22.667px` |
| "পাসওয়ার্ড ভুলে গেছেন?" link | font `16.667px` Regular, color `#0f6e56` (action-green) |
| Submit button | height `58.667px`, full width (minus `53.33px` side margins), bg `#063d2c`, radius `10.667px`; icon + text "প্রবেশ করুন" `19.333px` Medium white |
| Notice/info box | height `85px`, bg `#eff9f5` (= `icon-bg-green` token), border `1.333px #b8e0d2`, radius `10.667px`; icon + text `16px` Regular, color `#0b5a45`, line-height `26.4px` |
| Footer copyright (below card, on dark bg) | font `14.667px` Regular, white, centered |

### Surah List Page — table-based list, page shell same as Dashboard

| Element | Spec |
|---|---|
| Header bar | title "সূরার তালিকা" `22.667px` Medium `#221f1a`; subtitle "মোট ১১৪টি সূরা · ৬,২৩৬ আয়াত" `16px` Regular `#a09c94` |
| Search input (header, top-right) | bg `#f4f2ee`, border `1.333px #e0ddd6`, radius `9.333px`, height `50.667px`, width `266.667px` |
| Sort/filter icon button (header) | `104px` wide split-button, border `1.333px #e0ddd6`, radius `9.333px`; right half active state bg `#063d2c` |
| Filter pill row | bg white, border-bottom `1.333px #ece8df`, height `78.67px` |
| — active pill | bg `#063d2c`, radius `26.667px`, height `42.667px`, text white `16.667px` Medium — e.g. "সব (১১৪)" |
| — inactive pill | bg white, border `1.333px #e0ddd6`, radius `26.667px`, height `45.333px`, text `#5a5750` `16.667px` Medium — "সম্পন্ন (১২)" / "চলমান (৮)" / "বাকি (৯৪)" |
| — vertical divider (between filter groups) | `1.333px` wide, bg `#e0ddd6`, height `29.333px` |
| — Mokki/Modani pills | same inactive-pill style — "মক্কী (৮৬)" / "মদনী (২৮)" |
| Table container | bg white, border `1.333px #e0ddd6`, radius `13.333px`, top margin `26.67px` |
| Table header row | bg `#faf9f5`, border-bottom `1.333px #ece8df`, height `69.333px`; labels "সূরা"/"অগ্রগতি"/"অবস্থা" font `14px` SemiBold, uppercase, tracking `0.4px`, color `#a09c94` |
| Table row | height `77.333px`, border-bottom `1.333px #f1eee7` |
| — surah-number circle | `37.333px`, radius `18.667px` (full), bg `#f1efe8`, number text `14.667px` SemiBold color `#5a5750` |
| — surah Arabic name | font `24px` (Figma: Amiri), color `#221f1a`, centered |
| — surah Bangla name | font `18px` Medium, color `#221f1a` |
| — meta text ("৭ আয়াত · মক্কী") | font `14.667px` Regular, color `#a09c94` |
| — progress bar track | height `5.333px`, radius `26.667px`, bg `#f0ede6` |
| — progress bar fill | bg `#1d9e75` (or gradient, consistent w/ Dashboard) |
| — progress % label | font `15.333px` Medium, color `#5a5750`, right-aligned |
| — status badge | height `32px`, radius `26.667px`, width auto (~`120px`); Final: bg `#e1f5ee` text `#085041`; Draft: bg `#faeeda` text `#633806`; Incomplete: bg `#f1efe8` text `#5a5750` — text `13.333px` SemiBold |

### Ayah View (`Surah to Ayat`) Page

| Element | Spec |
|---|---|
| Header (breadcrumb) | "সূরার তালিকা" `16.667px` Regular `#a09c94` + chevron + current "২ · আল-বাকারা" `16.667px` Medium `#221f1a` |
| Font-size toggle (header, right side) | label "ফন্ট সাইজ" `16px` Regular `#5a5750`; control bg `#f4f2ee` border `1.333px #ece8df` radius `9.333px` height `42.667px`; active size pill bg `#063d2c` radius `6.667px` text white `14.667px` SemiBold; inactive size text `#5a5750` `14.667px` Medium — controls Arabic word-grid font size (e.g. 14/16) |
| Content bg | `#f4f2ee`, top `83px`, left `293px` |
| **Ayah card** (one per ayah, stacked) | bg white, border `1.333px #ece8df`, radius `16px`, height varies with content |
| — ayah-number badge | height `40px`, bg `#063d2c`, radius `10.667px`, text `17.333px` Regular color `#c9a227` (Bangla numeral, e.g. "৬০") |
| — status badge (next to ayah number) | height `32px`, radius `26.667px`; Final: bg `#e1f5ee` text `#085041`; Draft: bg `#faeeda` text `#633806` |
| — word-grid item (per word) | Arabic word: font `34.667px` (Figma: Amiri), color `#221f1a`, centered; Bangla gloss below: font `14.667px` Regular, color `#8a867c`, centered — this is the reusable "word-by-word grid item" component |
| — horizontal divider (word-grid → translation) | height `1.333px`, bg `#f0ede6` |
| — translation block | label "অনুবাদ: " font `17.333px` Medium color `#a09c94`; translation text font `17.333px` Regular color `#221f1a`, line-height `31.2px` |
| **Prev/Next navigation buttons** (bottom, fixed) | height `45px`, bg `#0f6e56` (action-green), radius `8px`/`9.333px`; text white `16px` SemiBold + `«`/`»` arrow glyph — "পূর্ববর্তী আয়াত" / "পরবর্তী আয়াত" |

### Search Page

| Element | Spec |
|---|---|
| Header | title "অনুসন্ধান" `22.667px` Medium `#221f1a` |
| Query card | bg white, border `1.333px #ece8df`, radius `16px`, height `197.333px` |
| — label | "আরবি শব্দ লিখুন (ডায়াক্রিটিক্স ছাড়াই লেখা যাবে)" font `16px` Medium color `#5a5750` |
| — result-count text | font `16px` Regular color `#a09c94` — e.g. `১২৯টি আয়াতে "رحم" মূলধাতুযুক্ত শব্দ পাওয়া গেছে` |
| — Arabic input | bg `#f7f5ef`, border `1.333px #e0ddd6`, radius `12px`, height `66.667px`; text `26.667px` (Figma: Amiri), color `#221f1a`, right-aligned |
| Results table | bg white, border `1.333px #ece8df`, radius `16px`, height `426.667px` |
| — table header row | bg `#f7f5ef`, border-bottom `1.333px #ece8df`, height `57.333px`; labels "সূরা · আয়াত" / "আরবি টেক্সট" font `14.667px` SemiBold color `#8a867c` |
| — table row | height `92px`, border-bottom `1.333px #f4f1ea` |
| — surah·ayah label | font `16.667px` Medium color `#221f1a` — e.g. "১ · আল-ফাতিহা" |
| — ayah-number sub-label | font `15.333px` Regular color `#a09c94` — e.g. "আয়াত ৩" |
| — Arabic preview text | font `25.333px` (Figma: Amiri), color `#221f1a`, right-aligned |
| — **matched-word highlight** | bg `#fbf3d9` (= `icon-bg-gold` token), radius `4px`, wraps the matched Arabic word inline within the preview text |

### Word Dictionary Page

| Element | Spec |
|---|---|
| Header | title "শব্দ অভিধান" `22.667px` Medium `#221f1a`; subtitle "প্রতিটি ইউনিক শব্দের রুট, অর্থ ও ব্যাকরণগত তথ্য" `16px` Regular `#a09c94` |
| Search input (header, top-right) | bg `#f4f2ee`, border `1.333px #e0ddd6`, radius `10.667px`, height `50.667px`, width `306.667px`; placeholder "রুট বা শব্দ খুঁজুন…" `16.667px` Regular color `#a09c94` |
| Filter pill row | bg white, border-bottom `1.333px #ece8df`, height `78.67px` |
| — active pill | bg `#063d2c`, radius `26.667px`, height `42.667px`, text white `16.667px` Medium — "সব (৬,৮৩২)" |
| — inactive pill | bg white, border `1.333px #e0ddd6`, radius `26.667px`, height `45.333px`, text `#5a5750` `16.667px` Medium — "সম্পূর্ণ (২,১৪৭)" / "অসম্পূর্ণ (৪,৬৮৫)" |
| Table container | bg white, border `1.333px #ece8df`, radius `16px`, height `485.333px` |
| Table header row | bg `#f7f5ef`, border-bottom `1.333px #ece8df`, height `57.333px`; columns "শব্দ" / "রুট" / "ডিফল্ট অর্থ" / "পার্টস অফ স্পিচ" / "উপস্থিতি" / "অবস্থা" — font `14.667px` SemiBold color `#8a867c` |
| Table row | height `85.333px`, border-bottom `1.333px #f4f1ea` |
| — word column (Arabic) | font `26.667px` (Figma: Amiri), color `#221f1a` — e.g. "اللَّهُ" |
| — root column (Arabic letters) | font `20px` (Figma: Amiri), color `#5a5750`, right-aligned — e.g. "أ ل ه" |
| — default meaning (Bangla) | font `16.667px` Regular, color `#221f1a` |
| — part-of-speech (Bangla) | font `16px` Regular, color `#5a5750` |
| — occurrence count | font `16px` Regular, color `#5a5750` — e.g. "২,৬৯৯ বার" |
| — status badge | height `32px`, radius `26.667px`; Final: bg `#e1f5ee` text `#085041`; খসড়া/Draft: bg `#faeeda` text `#633806`; অসম্পূর্ণ/Incomplete: bg `#f1efe8` text `#5a5750` — font `14.667px` SemiBold |

### Repeated UI pattern (component candidate) — kon kon screen-e use hoyeche

| Component | Screens-e dekha gelo |
|---|---|
| Sidebar (logo + nav + tools + user footer) | Dashboard, Surah List, Ayah View, Word Dictionary, Search — **shob authenticated page-e identical** |
| Page header (title + subtitle) | Dashboard, Surah List, Word Dictionary, Search, Ayah View (breadcrumb variant) |
| Filter tabs / pill group (সব, সম্পূর্ণ, চলমান...) with count | Surah List, Word Dictionary |
| Status badge (Final/Draft/Incomplete — 3 color variants) | Surah List, Ayah View, Word Dictionary |
| Search input (icon + placeholder) | Word Dictionary (top-right), Search page (main, Arabic RTL variant), Surah List (header) |
| Data table (header row + rows) | Surah List, Word Dictionary, Search (results) |
| Progress bar + percentage | Surah List (per-row), Dashboard (stat cards) |
| Stat card | Dashboard |
| Ayah card (ruku badge + status + word grid + translation) | Ayah View |
| Word-by-word grid item (Arabic + Bangla gloss under) | Ayah View |
| Root-letters display (spaced Arabic letters) | Word Dictionary |
| Highlighted-match text span (inline bg on Arabic substring) | Search |
| Pagination | Dashboard (Recent Activity) |
| Activity list item (icon + text + relative time) | Dashboard |
| Prev/Next navigation button pair | Ayah View |
| Font-size toggle control | Ayah View |
| Auth card (logo header + form) | Login |
| Text input w/ icon (username, password w/ show-hide) | Login |
| Primary button | Login, Ayah View (Prev/Next) |
| Info/notice box | Login |

**Mane — 6-ta alada page hoile-o, UI building block matro ~19 ta.** Eigula
ekbar bhalo kore banale, baki shob page shudhu shei block-gula sajiye felei
hoye jabe.

---

## 2. Design System Setup — SOBAR AGE eta koro

Tumi Tailwind CSS v4 use korcho, tai `tailwind.config.js`-er bodole **CSS-first
`@theme`** approach use korbe (v4-er notun way). Shob color/font ekjaygay,
`src/index.css`-e:

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  /* Primary (brand green) — confirmed from Figma */
  --color-primary: #063d2c;

  /* Accent (gold) — confirmed from Figma */
  --color-accent: #c9a227;

  /* Action green (links, Prev/Next buttons) — same hex as progress-gradient-from */
  --color-action-green: #0f6e56;

  /* Surface / background — confirmed from Figma */
  --color-background: #f4f2ee;
  --color-surface: #ffffff;
  --color-surface-subtle: #f7f5ef;   /* Search input bg, Search/Word Dict table header */
  --color-surface-subtle-2: #faf9f5; /* Surah List table header — near-dup, kept distinct */
  --color-card-bg-alt: #fafaf8;      /* Login card bg */

  /* Borders — confirmed from Figma */
  --color-border: #ece8df;
  --color-border-subtle: #e0ddd6;    /* table/search-input borders */
  --color-border-input: #d4d0c8;     /* Login input border */

  /* Text — confirmed from Figma */
  --color-text-heading: #221f1a;
  --color-text-muted: #8a867c;
  --color-text-muted-2: #a09c94;
  --color-text-input: #757575;       /* Login input text */
  --color-text-pagination-inactive: #5a5750;

  /* Progress bars — confirmed from Figma */
  --color-progress-track: #eeebe4;       /* Dashboard */
  --color-progress-track-2: #f0ede6;     /* Surah List row — near-dup, kept distinct */
  --color-progress-gradient-from: #0f6e56;
  --color-progress-gradient-to: #1d9e75;

  /* Icon / highlight backgrounds (soft tints) — confirmed from Figma */
  --color-icon-bg-green: #eff9f5;    /* also Login notice-box bg */
  --color-icon-bg-gold: #fbf3d9;     /* also Search matched-word highlight */
  --color-avatar-neutral-bg: #f1efe8; /* Surah List ruku circle, neutral status badge bg */

  --color-divider: #f1eee7;          /* Dashboard activity row divider, Surah List row border */
  --color-row-divider: #f4f1ea;      /* Search / Word Dictionary row border */

  /* Login-specific notice box */
  --color-notice-border: #b8e0d2;
  --color-notice-text: #0b5a45;

  /* Sidebar (dark bg, so text/border use alpha over white) — confirmed */
  --color-sidebar-border: rgba(255,255,255,0.08);
  --color-sidebar-text-inactive: rgba(255,255,255,0.55);
  --color-sidebar-text-label: rgba(255,255,255,0.32);
  --color-sidebar-active-bg: rgba(255,255,255,0.1);
  --color-logo-badge-bg: rgba(201,162,39,0.14);
  --color-logo-badge-border: rgba(201,162,39,0.4);
  --color-login-pill-bg: rgba(201,162,39,0.06);
  --color-login-pill-border: rgba(201,162,39,0.55);

  /* Status badges — CONFIRMED (3 variants, used on Surah List / Ayah View / Word Dictionary) */
  --color-status-success-bg:   #e1f5ee;
  --color-status-success-text: #085041;
  --color-status-warning-bg:   #faeeda;
  --color-status-warning-text: #633806;
  --color-status-neutral-bg:   #f1efe8;
  --color-status-neutral-text: #5a5750;

  /* Fonts — Bangla is PAGE-SPECIFIC (apatoto, follows mockup — see ⚠️ box
     at top of this document); Arabic is a confirmed override (QPC Hafs,
     not Figma's Amiri) applied everywhere */
  --font-bangla-login: "Noto Sans Bengali", sans-serif;   /* Login page only */
  --font-bangla: "Hind Siliguri", sans-serif;              /* all other pages */
  --font-arabic: "QPC Hafs", serif;                        /* all pages */

  /* Radius scale seen across cards — confirmed from Figma */
  --radius-card-sm: 16px;
  --radius-card-lg: 18.667px;
  --radius-card-table: 13.333px;
  --radius-pill: 26.667px;
  --radius-nav-item: 10.667px;
  --radius-icon-box: 13.333px;
  --radius-input: 10.667px;
  --radius-search-input: 9.333px;

  /* Shadows — confirmed from Figma */
  --shadow-card: 0px 26.667px 80px 0px rgba(0,0,0,0.15);
  --shadow-login-card: 0px 40px 106.667px 0px rgba(0,0,0,0.35);
}
```

Eta likhle Tailwind automatically `bg-primary-700`, `text-accent-500`,
`bg-status-success-bg` — ei rokom utility class generate kore dibe. **Tumi
jetake "globally fix kore rakhbo" bolechile, eta-i sheta** — color ekjaygay
(`@theme` block-e) define, baki shob component shudhu class name reference
kore, direct hex code kothao lekha thakbe na.

**Note on near-duplicate off-white/border tones:** Figma file-e kichu kichu
jaygay prai-eki dekhte 2-3 ta off-white/gray tone alada value hishebe ache
(e.g. `#f7f5ef` vs `#faf9f5`, `#eeebe4` vs `#f0ede6`, `#f1eee7` vs `#f4f1ea`).
Eগুলো designer-er ভুল-o hote pare, abar intentional subtle variation-o hote
pare. Ei document-e **eguলো merge na kore alada token hishebe rakha hoyeche**
(jeta actually Figma-e ache), karon merge korle visual drift hote pare —
implementation-er shomoy dorkar hole client-ke jiggesh kore ekta consolidate
kora jete pare.

Button-e kivabe use hobe, example:

```jsx
// src/components/ui/Button.jsx
export default function Button({ variant = 'primary', children, ...props }) {
  const variants = {
    primary: 'bg-primary-700 hover:bg-primary-800 text-white',
    action: 'bg-action-green-700 hover:bg-action-green-800 text-white',
    outline: 'border border-primary-700 text-primary-700 hover:bg-primary-50',
    ghost: 'text-primary-700 hover:bg-primary-50',
  };
  return (
    <button
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${variants[variant]}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

Ekhon kono din brand color change korte hole, `@theme`-er 2-3 line change
korlei — Button, Badge, Sidebar, sob jaygay automatically update hobe. Kono
component-e hardcoded hex kothao lekha thakbe na.

---

## 3. Reusable UI Component Library (`src/components/ui/`)

| Component | Kaj | Props (sketch) |
|---|---|---|
| `Button.jsx` | Primary/action/outline/ghost button | `variant`, `size`, `icon` |
| `Badge.jsx` | Status pill (Final/Draft/Incomplete — 3 color variants) | `status: 'success' \| 'warning' \| 'neutral'` |
| `Card.jsx` | White rounded container w/ border+shadow | `children`, `padding` |
| `Input.jsx` | Text input w/ optional icon (left/right), show-hide for password | `icon`, `type`, error state |
| `SearchInput.jsx` | `Input` + search icon, debounced onChange | `onSearch` |
| `ArabicInput.jsx` | RTL Arabic text input (Search page query box) | `value`, `onChange` |
| `Table.jsx` | Header + rows wrapper, consistent spacing | `columns`, `data` |
| `ProgressBar.jsx` | Colored bar + percentage label | `value`, `max`, `color` |
| `Tabs.jsx` (filter pills) | Active/inactive pill group w/ count | `tabs: [{label, count}]` |
| `Pagination.jsx` | Page number nav | `page`, `totalPages`, `onChange` |
| `Avatar.jsx` | Circle initial-based avatar (gold bg) | `name` |
| `WordGridItem.jsx` | Arabic word + Bangla gloss stacked, centered | `arabic`, `gloss` |
| `RootLetters.jsx` | Spaced Arabic root-letter display | `letters: string[]` |
| `HighlightedText.jsx` | Arabic text w/ inline highlighted substring | `text`, `matchStart`, `matchEnd` |
| `NoticeBox.jsx` | Icon + text info/warning box (Login) | `icon`, `children`, `variant` |
| `FontSizeToggle.jsx` | 2-option pill toggle (Ayah View font size) | `value`, `options`, `onChange` |

## 4. Layout Components (`src/components/layout/`)

| Component | Kaj |
|---|---|
| `Sidebar.jsx` | Logo + nav (প্রধান মেনু, টুলস sections) + user footer — ekbar bananor por shob authenticated page-e reuse |
| `AppShell.jsx` | Sidebar + main content area wrapper, route `<Outlet />` |
| `AuthLayout.jsx` | Login page-er jonno alada centered-card layout (Sidebar nei) |
| `ProtectedRoute.jsx` | JWT token check kore route guard kore |

## 5. Page → Component mapping (development-er shomoy checklist hishebe use koro)

| Page | Use kora component |
|---|---|
| Login | `AuthLayout`, `Input`, `Button`, `NoticeBox` |
| Dashboard | `AppShell`, `Card` (stat cards), `ProgressBar`, activity list item, `Pagination`, `Tabs` (time range) |
| Surah List | `AppShell`, `Tabs`, `SearchInput`, `Table`, `ProgressBar`, `Badge`, `Avatar` (surah-number circle) |
| Ayah View (Surah detail) | `AppShell`, `Badge`, `WordGridItem`, `Button` (prev/next), `FontSizeToggle` |
| Word Dictionary | `AppShell`, `Tabs`, `SearchInput`, `Table`, `Badge`, `RootLetters` |
| Search | `AppShell`, `ArabicInput`, `Table`, `HighlightedText` |

---

## 6. Recommended Build Order (phased)

**Phase 0 — Foundation (1-2 din-er kaj, kintu sobcheye important)**
1. Vite + React scaffold, Tailwind v4 install, `@theme` token setup (upor-e deya)
2. Font setup: **QPC Hafs** load live from Quran Foundation's own CDN
   (Arabic, all pages) — self-host **korbe na**, QF corrections push kore
   font file-e time-to-time; **Hind Siliguri** + **Noto Sans Bengali** load
   kora jabe Google Fonts CDN theke (duitai Google Fonts-e ache, self-host
   lagbe na) — Login-e Noto Sans Bengali, baki page-e Hind Siliguri
3. Base UI components: `Button`, `Badge`, `Card`, `Input`, `ProgressBar`
4. `react-router-dom` + `axios` setup, `.env` (`VITE_API_BASE_URL`)

**Phase 1 — Auth**
1. `AuthLayout` + Login page (UI only, mock submit)
2. Backend JWT endpoint wire-up (login → access+refresh token store, axios interceptor)
3. `ProtectedRoute` guard

**Phase 2 — App shell**
1. `Sidebar` + `AppShell` (routing skeleton, sob nav item just empty page-e point kore rakhbe prothome)

**Phase 3 — Dashboard**
- Stat card, progress card, Recent Activity list + pagination (API already
  thakle real data, na thakle mock diye UI age banao)

**Phase 4 — Surah List**
- `Tabs` + `Table` + `Badge` + `ProgressBar` — ei phase-e `Table` component
  mature hoye jabe, porer page-e (Word Dictionary) reuse shohoj hobe

**Phase 5 — Ayah View**
- Sobcheye complex page — word-by-word grid, ruku badge, translation
  display, font-size toggle, Prev/Next navigation. Font (QPC Hafs) ekhane
  properly test hobe.

**Phase 6 — Word Dictionary**
- Phase 4-er `Table`/`Tabs`/`Badge` reuse kore fast build hobe, `RootLetters`
  notun component

**Phase 7 — Search**
- `ArabicInput` + result `Table` + `HighlightedText` (matched-word highlight logic)

---

## Note

**Shob 6-ta page** (Dashboard, Sidebar, Login, Surah List, Ayah View,
Word Dictionary, Search) — color/spacing/radius/font-size shob value ekhon
✅ **CONFIRMED**, Figma MCP diye direct pull kora (section 1.5 dekho). Ar
kono approximate/estimate value ei document-e nei.

**Mone rekho (font):** Bangla font **page-onujayi mockup follow kore**
(apatoto) — Login-e Noto Sans Bengali, baki page-e Hind Siliguri. Arabic
font-er jonno shudhu **QPC Hafs** use korte hobe (Amiri na) — eta ekmatro
confirmed override. Dekho ⚠️ box, document-er shuru-te.