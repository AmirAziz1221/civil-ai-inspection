import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  History, ScanLine, ArrowRight, Search, Filter,
  Download, FileText, Loader2, AlertCircle, RefreshCw
} from 'lucide-react'
import { getInspections } from '../api/client.js'
import { format, parseISO } from 'date-fns'
import clsx from 'clsx'

const SEVERITY_CONFIG = {
  Critical: { badge: 'badge-critical', dot: 'bg-red-500' },
  High:     { badge: 'badge-high',     dot: 'bg-orange-500' },
  Medium:   { badge: 'badge-medium',   dot: 'bg-amber-500' },
  Low:      { badge: 'badge-low',      dot: 'bg-green-500' },
}

const MODEL_LABELS = {
  facade:    'Facade',
  asphalt:   'Asphalt',
  concrete:  'Concrete/Bridge',
  pv:        'PV Panels',
  powerline: 'Powerline',
  slopes:    'Slopes',
}

export default function HistoryPage() {
  const [inspections, setInspections] = useState([])
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState('')
  const [search, setSearch]           = useState('')
  const [filterSeverity, setFilter]   = useState('All')
  const navigate = useNavigate()

  const API_BASE = import.meta.env.VITE_API_URL || '/api'

  const load = () => {
    setLoading(true)
    getInspections()
      .then(r => setInspections(r.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const filtered = inspections.filter(i => {
    const matchSearch = !search ||
      i.original_filename?.toLowerCase().includes(search.toLowerCase()) ||
      i.asset_type?.toLowerCase().includes(search.toLowerCase()) ||
      i.model_name?.toLowerCase().includes(search.toLowerCase())
    const matchSev = filterSeverity === 'All' || i.overall_severity === filterSeverity
    return matchSearch && matchSev
  })

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Inspection History</h1>
          <p className="text-sm text-slate-500 mt-0.5">{inspections.length} inspections total</p>
        </div>
        <button onClick={load} className="btn-secondary">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by file, asset type, model…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input pl-8"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-slate-400" />
          <select
            value={filterSeverity}
            onChange={e => setFilter(e.target.value)}
            className="input w-auto"
          >
            {['All', 'Critical', 'High', 'Medium', 'Low'].map(s => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="p-12 flex flex-col items-center gap-3 text-slate-400">
            <Loader2 size={24} className="animate-spin" />
            <span className="text-sm">Loading inspections…</span>
          </div>
        ) : error ? (
          <div className="p-8 flex flex-col items-center gap-2 text-red-500">
            <AlertCircle size={24} />
            <span className="text-sm">{error}</span>
            <button onClick={load} className="btn-secondary mt-2">Retry</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center">
            <History size={40} className="text-slate-200 mx-auto mb-3" />
            <p className="text-slate-500 text-sm font-medium">
              {inspections.length === 0 ? 'No inspections yet' : 'No results match your filters'}
            </p>
            {inspections.length === 0 && (
              <button onClick={() => navigate('/inspect')} className="btn-primary mt-3">
                Start First Inspection
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  {['File', 'Asset Type', 'Model', 'Defects', 'Severity', 'Date', 'Reports', ''].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {filtered.map(insp => {
                  const sevCfg = SEVERITY_CONFIG[insp.overall_severity] || SEVERITY_CONFIG.Low
                  const hasReport = insp.report_docx || insp.report_pdf
                  return (
                    <tr
                      key={insp.id}
                      className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                      onClick={() => navigate(`/inspection/${insp.id}`)}
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded bg-brand-50 flex items-center justify-center flex-shrink-0">
                            <ScanLine size={13} className="text-brand-600" />
                          </div>
                          <span className="font-medium text-slate-800 max-w-[180px] truncate">
                            {insp.original_filename || '—'}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-slate-600 whitespace-nowrap">
                        {insp.asset_type || '—'}
                      </td>
                      <td className="px-4 py-3 text-slate-500 text-xs">
                        {MODEL_LABELS[insp.model_name] || insp.model_name || '—'}
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-semibold text-slate-800">{insp.total_defects ?? 0}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`badge ${sevCfg.badge}`}>{insp.overall_severity || 'N/A'}</span>
                      </td>
                      <td className="px-4 py-3 text-slate-400 text-xs whitespace-nowrap">
                        {insp.created_at
                          ? format(parseISO(insp.created_at), 'MMM d, yyyy HH:mm')
                          : '—'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1.5" onClick={e => e.stopPropagation()}>
                          {insp.report_docx && (
                            <a
                              href={`${API_BASE}/download/docx/${insp.id}`}
                              download
                              target="_blank" rel="noreferrer"
                              className="p-1.5 rounded-md hover:bg-blue-50 text-blue-600 transition-colors"
                              title="Download Word"
                            >
                              <FileText size={14} />
                            </a>
                          )}
                          {insp.report_pdf && (
                            <a
                              href={`${API_BASE}/download/pdf/${insp.id}`}
                              download
                              target="_blank" rel="noreferrer"
                              className="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 transition-colors"
                              title="Download PDF"
                            >
                              <Download size={14} />
                            </a>
                          )}
                          {!hasReport && (
                            <span className="text-xs text-slate-300">No report</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <ArrowRight
                          size={14}
                          className="text-slate-300 group-hover:text-brand-500 transition-colors"
                        />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
