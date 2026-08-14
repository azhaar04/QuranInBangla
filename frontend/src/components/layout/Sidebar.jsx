import { NavLink } from 'react-router-dom'
import {
  BookMarked,
  BookOpen,
  LayoutDashboard,
  ListOrdered,
  LogOut,
  Search,
} from 'lucide-react'
import Logo from '../ui/Logo'
import { useAuth } from '../../context/AuthContext'

const MAIN_NAV = [
  { label: 'ড্যাশবোর্ড', icon: LayoutDashboard, to: '/', end: true },
  { label: 'সূরার তালিকা', icon: BookOpen, to: '/surahs' },
  { label: 'রুকুর তালিকা', icon: ListOrdered, to: '/rukus' },
  { label: 'শব্দ অভিধান', icon: BookMarked, to: '/dictionary' },
]

const TOOLS_NAV = [{ label: 'অনুসন্ধান', icon: Search, to: '/search' }]

function NavItem({ label, icon: Icon, to, end }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `relative flex h-14 items-center gap-3 rounded-[10.667px] px-[14.67px] text-[17.333px] transition-colors ${
          isActive
            ? 'bg-sidebar-active font-semibold text-white'
            : 'font-medium text-sidebar-inactive hover:text-white'
        }`
      }
    >
      {({ isActive }) => (
        <>
          <Icon className="h-[21.333px] w-[21.333px] shrink-0" />
          <span>{label}</span>
          {isActive && (
            <span className="absolute right-0 top-1/2 h-full w-[2.667px] -translate-y-1/2 rounded-[2.667px] bg-gold" />
          )}
        </>
      )}
    </NavLink>
  )
}

export default function Sidebar() {
  const { username, logout } = useAuth()
  const initial = username ? username[0].toUpperCase() : '?'

  return (
    <aside className="flex h-svh w-[293.333px] shrink-0 flex-col bg-brand-dark">
      <div className="flex items-center gap-4 border-b-[1.333px] border-sidebar-line px-6 py-5">
        <div className="flex h-[50.667px] w-[50.667px] shrink-0 items-center justify-center rounded-xl border-[1.333px] border-logo-badge-border bg-logo-badge">
          <Logo size={26} />
        </div>
        <span className="text-[17.333px] font-semibold whitespace-nowrap">
          <span className="text-gold">Quran</span>{' '}
          <span className="text-white">in</span>{' '}
          <span className="text-gold">Bangla</span>
        </span>
      </div>

      <nav className="flex flex-1 flex-col gap-6 overflow-y-auto px-4 py-6">
        <div className="flex flex-col gap-1">
          <span className="px-[10.67px] text-[13.333px] font-semibold tracking-[1.0667px] text-sidebar-label uppercase">
            প্রধান মেনু
          </span>
          {MAIN_NAV.map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </div>
        <div className="flex flex-col gap-1">
          <span className="px-[10.67px] text-[13.333px] font-semibold tracking-[1.0667px] text-sidebar-label uppercase">
            টুলস
          </span>
          {TOOLS_NAV.map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </div>
      </nav>

      <div className="flex items-center gap-3 border-t-[1.333px] border-sidebar-line px-6 py-5">
        <span className="flex h-[45.333px] w-[45.333px] shrink-0 items-center justify-center rounded-full bg-gold text-[17.333px] font-bold text-brand-dark">
          {initial}
        </span>
        <div className="min-w-0 flex-1 leading-tight">
          <p className="truncate text-[16.667px] font-medium text-white">{username}</p>
          <p className="text-[14px] text-gold">Admin</p>
        </div>
        <button
          type="button"
          onClick={logout}
          className="shrink-0 text-sidebar-inactive hover:text-white"
          aria-label="লগ-আউট"
        >
          <LogOut className="h-[21.333px] w-[21.333px]" />
        </button>
      </div>
    </aside>
  )
}
