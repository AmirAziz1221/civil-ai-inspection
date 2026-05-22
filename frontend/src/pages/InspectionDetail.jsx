import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Download, FileText, ScanLine, AlertTriangle,
  CheckCircle, Loader2, Info, Calendar, Cpu, ImageIcon,
  Clipboard, Shield
} from 'lucide-react'
import { getInspection } from '../api/client.js'
import { format, parseISO } from 'date-fns'
import clsx from 'clsx'

const SEVERITY_CONFIG = {
  Critical: { badge: 'badge-critical', bar: 'bg-red-500' },
  High:     { badge: 'badge-high',     bar: 'bg-orange-500' },
  Medium:   { badge: 'badge-medium',   bar: 'bg-amber-500' },
  Low:      { badge: 'badge-low',      bar: 'bg-green-500' },
}

function Section({ title, icon: Icon, children }) {
  return (
    <div className="card overflow-hidden">
      <div className="flex items-center gap-2 px-5 py-4 border-b border-slate-100 bg-slate-50/60">
        <Icon size={15} className="text-brand-600" />
        <h3 className="text-sm font-semibold text-slate-700">{title}</h3>
      </div>
      <div className="p-5">{children}</div>
    </div>
  )
}

function InfoRow({ label, value }) {
  return (
    <div className="flex flex-wrap gap-1 py-2 border-b border-slate-50 last:border-0">
      <span className="text-xs font-medium text-slate-500 w-36 flex-shrink-0">{label}</span>
      <span className="text-sm text-slate-800 flex-1">{value || '—'}</span>
    </div>
  )
}

export default function InspectionDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [insp, setInsp]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState('')

  const API_BASE = import.meta.env.VITE_API_URL || '/api'

  useEffect(() => {
    getInspection(id)
      .then(r => setInsp(r.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="p-12 flex flex-col items-center gap-3 text-slate-400">
      <Loader2 size={28} className="animate-spin" />
      <span className="text-sm">Loading inspection…</span>
    </div>
  )

  if (error) return (
    <div className="p-12 text-center text-red-500">
      <AlertTriangle size={28} className="mx-auto mb-2" />
      <p className="text-sm">{error}</p>
      <button onClick={() => navigate('/history')} className="btn-secondary mt-4">
        <ArrowLeft size={14} /> Back to History
      </button>
    </div>
  )

  if (!insp) return null

  const ai = insp.ai_report || {}
  const sev = insp.severity_summary || {}
  const sevCfg = SEVERITY_CONFIG[insp.overall_severity] || SEVERITY_CONFIG.Low
  const total = insp.total_defects || 0

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/history')}
            className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-2 transition-colors"
          >
            <ArrowLeft size={14} /> Back to History
          </button>
          <h1 className="text-xl font-bold text-slate-900">Inspection Report</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            ID: <span className="font-mono text-xs">{id.slice(0, 8).toUpperCase()}</span>
            {insp.created_at && (
              <span className="ml-2">
                · {format(parseISO(insp.created_at), 'MMMM d, yyyy, HH:mm')} UTC
              </span>
            )}
          </p>
        </div>

        {/* Download buttons */}
        {(insp.report_docx || insp.report_pdf) && (
          <div className="flex items-center gap-2 flex-shrink-0">
            {insp.report_docx && (
              <a
                href={`${API_BASE}/download/docx/${id}`}
                download
                target="_blank" rel="noreferrer"
                className="btn-primary text-xs"
              >
                <Download size={13} /> Word
              </a>
            )}
            {insp.report_pdf && (
              <a
                href={`${API_BASE}/download/pdf/${id}`}
                download
                target="_blank" rel="noreferrer"
                className="btn-secondary text-xs"
              >
                <Download size={13} /> PDF
              </a>
            )}
          </div>
        )}
      </div>

      {/* Severity banner */}
      <div className={clsx(
        'rounded-xl border p-4 flex items-center gap-3',
        insp.overall_severity === 'Critical' && 'bg-red-50 border-red-200',
        insp.overall_severity === 'High'     && 'bg-orange-50 border-orange-200',
        insp.overall_severity === 'Medium'   && 'bg-amber-50 border-amber-200',
        insp.overall_severity === 'Low'      && 'bg-green-50 border-green-200',
      )}>
        <AlertTriangle size={20} className={clsx(
          insp.overall_severity === 'Critical' && 'text-red-500',
          insp.overall_severity === 'High'     && 'text-orange-500',
          insp.overall_severity === 'Medium'   && 'text-amber-500',
          insp.overall_severity === 'Low'      && 'text-green-500',
        )} />
        <div>
          <div className="font-semibold text-slate-800 text-sm">
            Overall Severity: {insp.overall_severity || 'N/A'}
          </div>
          <div className="text-xs text-slate-500 mt-0.5">
            {total} defect{total !== 1 ? 's' : ''} detected ·
            Prepared for <strong>Dani</strong> · {insp.asset_type}
          </div>
        </div>
        <span className={`ml-auto badge ${sevCfg.badge}`}>
          {insp.overall_severity}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column */}
        <div className="space-y-6 lg:col-span-1">
          {/* Project info */}
          <Section title="Project Information" icon={Info}>
            <InfoRow label="Client" value="Dani" />
            <InfoRow label="Asset Type" value={insp.asset_type} />
            <InfoRow label="Detection Model" value={insp.model_name} />
            <InfoRow label="Image File" value={insp.original_filename} />
            <InfoRow label="Total Defects" value={String(total)} />
            <InfoRow label="Inspection ID" value={id.slice(0, 8).toUpperCase()} />
          </Section>

          {/* Severity summary */}
          <Section title="Severity Breakdown" icon={AlertTriangle}>
            {Object.entries(sev).map(([severity, count]) => {
              const cfg = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.Low
              const pct = total > 0 ? Math.round((count / total) * 100) : 0
              return (
                <div key={severity} className="mb-3 last:mb-0">
                  <div className="flex justify-between text-xs mb-1">
                    <span className={`badge ${cfg.badge}`}>{severity}</span>
                    <span className="text-slate-500">{count} ({pct}%)</span>
                  </div>
                  <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full ${cfg.bar} rounded-full`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              )
            })}
          </Section>

          {/* Engineer notes */}
          {insp.engineer_notes && (
            <Section title="Engineer Notes" icon={Clipboard}>
              <p className="text-sm text-slate-600 leading-relaxed">{insp.engineer_notes}</p>
            </Section>
          )}
        </div>

        {/* Right column */}
        <div className="space-y-6 lg:col-span-2">
          {/* Images */}
          <Section title="Visual Evidence" icon={ImageIcon}>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { label: 'Original Image', url: insp.image_id ? null : null, isAnnotated: false },
              ].map(({ label }) => null)}

              {insp.annotated_image && (
                <div>
                  <p className="text-xs font-medium text-slate-500 mb-2">Annotated (AI Detection)</p>
                  <img
                    src={`${API_BASE.replace('/api', '')}${insp.annotated_image}`}
                    alt="Annotated"
                    className="rounded-lg w-full object-contain bg-slate-50 border border-slate-100"
                    style={{ maxHeight: '220px' }}
                  />
                </div>
              )}
            </div>
          </Section>

          {/* Detection table */}
          {insp.detections?.length > 0 && (
            <Section title="Detected Pathologies" icon={ScanLine}>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      {['#', 'Defect Class', 'Confidence', 'Severity', 'Bounding Box'].map(h => (
                        <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-slate-500">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {insp.detections.map((d, i) => (
                      <tr key={i} className="hover:bg-slate-50/50">
                        <td className="px-3 py-2 text-slate-400 text-xs">{i + 1}</td>
                        <td className="px-3 py-2 font-medium text-slate-700 capitalize">
                          {d.class?.replace(/_/g, ' ')}
                        </td>
                        <td className="px-3 py-2">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-brand-500 rounded-full"
                                style={{ width: `${(d.confidence * 100).toFixed(0)}%` }}
                              />
                            </div>
                            <span className="font-mono text-xs text-slate-600">
                              {(d.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        </td>
                        <td className="px-3 py-2">
                          <span className={`badge badge-${d.severity?.toLowerCase()}`}>{d.severity}</span>
                        </td>
                        <td className="px-3 py-2 font-mono text-xs text-slate-400">
                          {d.bbox ? `[${d.bbox.join(', ')}]` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>
          )}

          {/* AI Report sections */}
          {Object.keys(ai).length > 0 && (
            <>
              {[
                { key: 'executive_summary',   title: 'Executive Summary',              icon: FileText },
                { key: 'defect_descriptions', title: 'Defect Descriptions',            icon: ScanLine },
                { key: 'possible_causes',     title: 'Possible Causes',               icon: Info },
                { key: 'severity_assessment', title: 'Severity Assessment',            icon: AlertTriangle },
                { key: 'risk_explanation',    title: 'Risk Assessment',               icon: AlertTriangle },
                { key: 'recommended_actions', title: 'Recommended Actions',            icon: CheckCircle },
                { key: 'priority_level',      title: 'Priority Level',                icon: Cpu },
                { key: 'final_conclusion',    title: 'Final Conclusion',              icon: FileText },
              ].map(({ key, title, icon }) => ai[key] && (
                <Section key={key} title={title} icon={icon}>
                  <p className="text-sm text-slate-600 leading-relaxed">{ai[key]}</p>
                </Section>
              ))}
            </>
          )}

          {/* Disclaimer */}
          <div className="flex items-start gap-3 p-4 rounded-xl bg-slate-50 border border-slate-200">
            <Shield size={16} className="text-slate-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-slate-500 leading-relaxed">
              <strong className="text-slate-600">Disclaimer:</strong> This AI-generated report is for preliminary
              inspection support only. All findings must be verified by a qualified, licensed civil engineer
              before any remediation decisions are made.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
