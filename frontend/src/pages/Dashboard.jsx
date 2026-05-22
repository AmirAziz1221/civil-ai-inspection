import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ScanLine, AlertTriangle, CheckCircle, Clock,
  TrendingUp, ArrowRight, FileText, Zap
} from 'lucide-react'
import { getInspections } from '../api/client.js'
import { format, parseISO } from 'date-fns'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts'

const SEVERITY_CONFIG = {
  Critical: { color: '#dc2626', bg: 'bg-red-50',    border: 'border-red-200',    text: 'text-red-700'   },
  High:     { color: '#ea580c', bg: 'bg-orange-50',  border: 'border-orange-200', text: 'text-orange-700' },
  Medium:   { color: '#d97706', bg: 'bg-amber-50',   border: 'border-amber-200',  text: 'text-amber-700'  },
  Low:      { color: '#16a34a', bg: 'bg-green-50',   border: 'border-green-200',  text: 'text-green-700'  },
}

function StatCard({ icon: Icon, label, value, sub, color = 'text-brand-600', bg = 'bg-brand-50' }) {
  return (
    <div className="card p-5 flex items-start gap-4">
      <div className={`w-10 h-10 rounded-lg ${bg} flex items-center justify-center flex-shrink-0`}>
        <Icon size={20} className={color} />
      </div>
      <div>
        <div className="text-2xl font-bold text-slate-900 leading-tight">{value}</div>
        <div className="text-sm font-medium text-slate-600">{label}</div>
        {sub && <div className="text-xs text-slate-400 mt-0.5">{sub}</div>}
      </div>
    </div>
  )
}

function SeverityBadge({ severity }) {
  const cfg = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.Low
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${cfg.bg} ${cfg.text} border ${cfg.border}`}>
      {severity}
    </span>
  )
}

export default function Dashboard() {
  const [inspections, setInspections] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getInspections()
      .then(r => setInspections(r.data))
      .catch(() => setInspections([]))
      .finally(() => setLoading(false))
  }, [])

  const totalDefects = inspections.reduce((s, i) => s + (i.total_defects || 0), 0)
  const criticalCount = inspections.filter(i => i.overall_severity === 'Critical').length
  const withReports = inspections.filter(i => i.report_docx || i.report_pdf).length

  // Chart data: defects by model
  const modelMap = {}
  inspections.forEach(i => {
    const m = i.model_name || 'unknown'
    modelMap[m] = (modelMap[m] || 0) + (i.total_defects || 0)
  })
  const chartData = Object.entries(modelMap).map(([name, count]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    defects: count
  }))

  const recent = inspections.slice(0, 6)

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            AI-assisted civil infrastructure inspection overview
          </p>
        </div>
        <button
          onClick={() => navigate('/inspect')}
          className="btn-primary"
        >
          <Zap size={16} />
          New Inspection
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={ScanLine}
          label="Total Inspections"
          value={inspections.length}
          sub="All time"
          color="text-brand-600"
          bg="bg-brand-50"
        />
        <StatCard
          icon={AlertTriangle}
          label="Total Defects"
          value={totalDefects}
          sub="Detected by AI"
          color="text-amber-600"
          bg="bg-amber-50"
        />
        <StatCard
          icon={AlertTriangle}
          label="Critical Findings"
          value={criticalCount}
          sub="Need immediate action"
          color="text-red-600"
          bg="bg-red-50"
        />
        <StatCard
          icon={FileText}
          label="Reports Generated"
          value={withReports}
          sub="Word & PDF"
          color="text-emerald-600"
          bg="bg-emerald-50"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart */}
        <div className="card p-5 lg:col-span-2">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Defects by Model</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData} barSize={32}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
                />
                <Bar dataKey="defects" radius={[4, 4, 0, 0]}>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill="#3b82f6" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-400 text-sm">
              No inspection data yet
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Quick Actions</h2>
          <div className="space-y-2">
            {[
              { label: 'New Facade Inspection',  path: '/inspect', model: 'facade'    },
              { label: 'New Road Inspection',    path: '/inspect', model: 'asphalt'   },
              { label: 'New Bridge Inspection',  path: '/inspect', model: 'concrete'  },
              { label: 'New PV Inspection',      path: '/inspect', model: 'pv'        },
              { label: 'New Slope Inspection',   path: '/inspect', model: 'slopes'    },
            ].map((a) => (
              <button
                key={a.label}
                onClick={() => navigate(a.path)}
                className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg
                           hover:bg-brand-50 text-sm text-slate-600 hover:text-brand-700
                           border border-transparent hover:border-brand-200
                           transition-all duration-150 group"
              >
                <span>{a.label}</span>
                <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Recent inspections */}
      <div className="card">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-700">Recent Inspections</h2>
          <button
            onClick={() => navigate('/history')}
            className="text-xs text-brand-600 hover:text-brand-700 font-medium flex items-center gap-1"
          >
            View all <ArrowRight size={12} />
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading…</div>
        ) : recent.length === 0 ? (
          <div className="p-8 text-center">
            <ScanLine size={32} className="text-slate-300 mx-auto mb-2" />
            <p className="text-slate-500 text-sm">No inspections yet.</p>
            <button onClick={() => navigate('/inspect')} className="btn-primary mt-3 text-xs">
              Start your first inspection
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-50">
            {recent.map((insp) => (
              <div
                key={insp.id}
                onClick={() => navigate(`/inspection/${insp.id}`)}
                className="flex items-center gap-4 px-5 py-3.5 hover:bg-slate-50 cursor-pointer transition-colors"
              >
                <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center flex-shrink-0">
                  <ScanLine size={14} className="text-brand-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-slate-800 truncate">
                    {insp.original_filename || 'Unknown file'}
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    {insp.asset_type} · {insp.total_defects} defect{insp.total_defects !== 1 ? 's' : ''}
                  </div>
                </div>
                <SeverityBadge severity={insp.overall_severity || 'Low'} />
                <div className="text-xs text-slate-400 hidden sm:block flex-shrink-0">
                  {insp.created_at
                    ? format(parseISO(insp.created_at), 'MMM d, HH:mm')
                    : '—'}
                </div>
                <ArrowRight size={14} className="text-slate-300 flex-shrink-0" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
