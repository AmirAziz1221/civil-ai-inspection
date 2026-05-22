import React, { useState } from 'react'
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Upload, History, Settings,
  ScanLine, ChevronRight, Menu, X, Shield
} from 'lucide-react'
import clsx from 'clsx'

import Dashboard from './pages/Dashboard.jsx'
import InspectionPage from './pages/InspectionPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import InspectionDetail from './pages/InspectionDetail.jsx'

const NAV_ITEMS = [
  { to: '/',           icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/inspect',    icon: Upload,           label: 'New Inspection' },
  { to: '/history',    icon: History,          label: 'Inspection History' },
]

function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/30 z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside className={clsx(
        'fixed top-0 left-0 h-full w-64 bg-white border-r border-slate-200 z-30',
        'flex flex-col transition-transform duration-200',
        'lg:translate-x-0 lg:static lg:z-auto',
        open ? 'translate-x-0' : '-translate-x-full'
      )}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-100">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
            <ScanLine size={16} className="text-white" />
          </div>
          <div>
            <div className="text-sm font-bold text-slate-900 leading-tight">CivilScan AI</div>
            <div className="text-xs text-slate-400">Prepared for Dani</div>
          </div>
          <button
            onClick={onClose}
            className="ml-auto lg:hidden text-slate-400 hover:text-slate-600"
          >
            <X size={18} />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={onClose}
              className={({ isActive }) =>
                clsx('sidebar-link', isActive && 'active')
              }
            >
              <Icon size={17} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-slate-100">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Shield size={12} />
            <span>AI-assisted inspection tool</span>
          </div>
          <div className="text-xs text-slate-300 mt-1">v1.0.0</div>
        </div>
      </aside>
    </>
  )
}

function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 gap-3 flex-shrink-0">
          <button
            className="lg:hidden p-1.5 rounded-lg hover:bg-slate-100 text-slate-500"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={20} />
          </button>
          <div className="flex items-center gap-1.5 text-sm text-slate-400">
            <ScanLine size={14} className="text-brand-600" />
            <span className="font-medium text-slate-700">CivilScan AI</span>
            <ChevronRight size={12} />
            <span>Infrastructure Pathology Detection</span>
          </div>
          <div className="ml-auto text-xs text-slate-400 hidden sm:block">
            Prepared for <span className="font-semibold text-brand-700">Dani</span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/"            element={<Dashboard />} />
            <Route path="/inspect"     element={<InspectionPage />} />
            <Route path="/history"     element={<HistoryPage />} />
            <Route path="/inspection/:id" element={<InspectionDetail />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  )
}
