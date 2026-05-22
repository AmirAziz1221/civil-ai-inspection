import React, { useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import {
  Upload, ScanLine, ChevronRight, CheckCircle, Loader2,
  AlertTriangle, FileText, Download, Cpu, Image as ImageIcon,
  RefreshCw, Wand2, Info
} from 'lucide-react'
import clsx from 'clsx'
import {
  uploadImage, runDetection, generateReport,
  getModels, getDownloadUrl
} from '../api/client.js'

const STEPS = ['Upload', 'Model', 'Detect', 'Report']

const SEVERITY_STYLE = {
  Critical: 'badge-critical',
  High:     'badge-high',
  Medium:   'badge-medium',
  Low:      'badge-low',
}

function StepIndicator({ current }) {
  return (
    <div className="flex items-center gap-0 mb-8">
      {STEPS.map((label, i) => {
        const state = i < current ? 'done' : i === current ? 'active' : 'pending'
        return (
          <React.Fragment key={label}>
            <div className="flex flex-col items-center">
              <div className={clsx(
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all',
                state === 'done'    && 'bg-brand-600 border-brand-600 text-white',
                state === 'active'  && 'bg-white border-brand-600 text-brand-600',
                state === 'pending' && 'bg-white border-slate-200 text-slate-400',
              )}>
                {state === 'done' ? <CheckCircle size={14} /> : i + 1}
              </div>
              <span className={clsx(
                'text-xs mt-1 font-medium',
                state === 'active' ? 'text-brand-600' : 'text-slate-400'
              )}>{label}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={clsx(
                'flex-1 h-0.5 mt-[-12px] mx-1 transition-colors',
                i < current ? 'bg-brand-600' : 'bg-slate-200'
              )} />
            )}
          </React.Fragment>
        )
      })}
    </div>
  )
}

function ModelCard({ model, selected, onSelect }) {
  return (
    <button
      onClick={() => onSelect(model.key)}
      disabled={!model.available}
      className={clsx(
        'text-left p-4 rounded-xl border-2 transition-all w-full',
        selected && 'border-brand-500 bg-brand-50',
        !selected && model.available && 'border-slate-200 hover:border-brand-300 bg-white hover:bg-brand-50/50',
        !model.available && 'border-slate-100 bg-slate-50 opacity-60 cursor-not-allowed',
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="font-semibold text-sm text-slate-800">{model.display_name}</div>
        {!model.available && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-slate-200 text-slate-500 flex-shrink-0">
            No .pt file
          </span>
        )}
        {model.available && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 flex-shrink-0">
            Ready
          </span>
        )}
      </div>
      <div className="text-xs text-slate-500 mt-1">{model.asset_type}</div>
      <div className="text-xs text-slate-400 mt-1.5 leading-relaxed">{model.description}</div>
    </button>
  )
}

export default function InspectionPage() {
  const [step, setStep]             = useState(0)
  const [file, setFile]             = useState(null)
  const [preview, setPreview]       = useState(null)
  const [uploadProgress, setProgress] = useState(0)
  const [uploadResult, setUpload]   = useState(null)
  const [models, setModels]         = useState([])
  const [selectedModel, setModel]   = useState('')
  const [assetType, setAssetType]   = useState('')
  const [detection, setDetection]   = useState(null)
  const [reportResult, setReport]   = useState(null)
  const [engineerNotes, setNotes]   = useState('')
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState('')

  const API_BASE = import.meta.env.VITE_API_URL || '/api'
  const navigate = useNavigate()

  useEffect(() => {
    getModels().then(r => setModels(r.data)).catch(() => {})
  }, [])

  const onDrop = useCallback((accepted) => {
    if (!accepted.length) return
    const f = accepted[0]
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setError('')
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg','.jpeg','.png','.bmp','.tiff'], 'video/*': ['.mp4','.avi','.mov'] },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024,
  })

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    try {
      const res = await uploadImage(file, setProgress)
      setUpload(res.data)
      setStep(1)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleModelConfirm = () => {
    if (!selectedModel) { setError('Please select a model'); return }
    const m = models.find(x => x.key === selectedModel)
    setAssetType(m?.asset_type || selectedModel)
    setError('')
    setStep(2)
  }

  const handleDetect = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await runDetection(uploadResult.image_id, selectedModel, assetType)
      setDetection(res.data)
      setStep(3)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReport = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await generateReport(detection.inspection_id, engineerNotes)
      setReport(res.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setStep(0); setFile(null); setPreview(null); setUpload(null)
    setModel(''); setDetection(null); setReport(null); setNotes(''); setError('')
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">New Inspection</h1>
        <p className="text-sm text-slate-500 mt-0.5">Upload an image and run AI pathology detection</p>
      </div>

      <StepIndicator current={step} />

      {error && (
        <div className="mb-4 flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          <AlertTriangle size={15} />
          {error}
        </div>
      )}

      {/* STEP 0: Upload */}
      {step === 0 && (
        <div className="card p-6">
          <h2 className="text-base font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Upload size={17} className="text-brand-600" /> Upload Image or Video
          </h2>

          <div
            {...getRootProps()}
            className={clsx(
              'border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all',
              isDragActive ? 'border-brand-400 bg-brand-50' : 'border-slate-300 hover:border-brand-300 hover:bg-slate-50'
            )}
          >
            <input {...getInputProps()} />
            {preview ? (
              <div>
                <img src={preview} alt="Preview" className="max-h-56 mx-auto rounded-lg object-contain mb-3" />
                <p className="text-sm font-medium text-slate-700">{file.name}</p>
                <p className="text-xs text-slate-400 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            ) : (
              <div>
                <ImageIcon size={40} className="text-slate-300 mx-auto mb-3" />
                <p className="text-sm font-medium text-slate-600">
                  {isDragActive ? 'Drop your file here' : 'Drag & drop or click to upload'}
                </p>
                <p className="text-xs text-slate-400 mt-1">JPG, PNG, BMP, TIFF, MP4, AVI · Max 100MB</p>
              </div>
            )}
          </div>

          {uploadProgress > 0 && uploadProgress < 100 && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>Uploading…</span><span>{uploadProgress}%</span>
              </div>
              <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-brand-500 transition-all" style={{ width: `${uploadProgress}%` }} />
              </div>
            </div>
          )}

          <div className="flex justify-end mt-5">
            <button onClick={handleUpload} disabled={!file || loading} className="btn-primary">
              {loading ? <><Loader2 size={15} className="animate-spin" /> Uploading…</> : <>Continue <ChevronRight size={15} /></>}
            </button>
          </div>
        </div>
      )}

      {/* STEP 1: Model Selection */}
      {step === 1 && (
        <div className="card p-6">
          <h2 className="text-base font-semibold text-slate-800 mb-1 flex items-center gap-2">
            <Cpu size={17} className="text-brand-600" /> Select Detection Model
          </h2>
          <p className="text-sm text-slate-500 mb-5">
            Choose the model that matches your asset type. Models without a .pt file run in demo mode.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-5">
            {models.map(m => (
              <ModelCard key={m.key} model={m} selected={selectedModel === m.key} onSelect={setModel} />
            ))}
          </div>

          {selectedModel && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-brand-50 border border-brand-100 text-brand-700 text-sm mb-5">
              <Info size={14} />
              Selected: <strong>{models.find(m => m.key === selectedModel)?.display_name}</strong>
            </div>
          )}

          <div className="flex justify-between">
            <button onClick={() => setStep(0)} className="btn-secondary">Back</button>
            <button onClick={handleModelConfirm} disabled={!selectedModel} className="btn-primary">
              Continue <ChevronRight size={15} />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Run Detection */}
      {step === 2 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-6">
            <h2 className="text-base font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <ImageIcon size={17} className="text-brand-600" /> Uploaded Image
            </h2>
            {preview && <img src={preview} alt="Preview" className="rounded-lg w-full object-contain max-h-72 bg-slate-50" />}
            <div className="mt-3 text-xs text-slate-500">
              <div>File: <span className="font-medium text-slate-700">{file?.name}</span></div>
              <div className="mt-1">Model: <span className="font-medium text-slate-700">
                {models.find(m => m.key === selectedModel)?.display_name}
              </span></div>
            </div>
          </div>

          <div className="card p-6 flex flex-col justify-between">
            <div>
              <h2 className="text-base font-semibold text-slate-800 mb-2 flex items-center gap-2">
                <ScanLine size={17} className="text-brand-600" /> Run Detection
              </h2>
              <p className="text-sm text-slate-500 mb-6">
                The AI model will analyse the image and identify all visible pathologies with bounding boxes, confidence scores, and severity ratings.
              </p>
              <div className="space-y-2 text-sm text-slate-600">
                {[
                  'Detect defect classes and locations',
                  'Calculate confidence scores',
                  'Assess severity levels',
                  'Generate annotated image',
                ].map(t => (
                  <div key={t} className="flex items-center gap-2">
                    <CheckCircle size={14} className="text-brand-500" />
                    {t}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-3 mt-6">
              <button onClick={handleDetect} disabled={loading} className="btn-primary justify-center py-3">
                {loading
                  ? <><Loader2 size={16} className="animate-spin" /> Analysing…</>
                  : <><Wand2 size={16} /> Run AI Detection</>}
              </button>
              <button onClick={() => setStep(1)} className="btn-secondary justify-center">Back</button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 3: Results & Report */}
      {step === 3 && detection && (
        <div className="space-y-6">
          {/* Results header */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {Object.entries(detection.severity_summary || {}).map(([sev, count]) => (
              <div key={sev} className="card p-4 text-center">
                <div className="text-2xl font-bold text-slate-900">{count}</div>
                <span className={`badge badge-${sev.toLowerCase()} mt-1`}>{sev}</span>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Annotated image */}
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">Annotated Detection</h3>
              {detection.annotated_image ? (
                <img
                  src={`${API_BASE.replace('/api', '')}${detection.annotated_image}`}
                  alt="Annotated"
                  className="rounded-lg w-full object-contain max-h-72 bg-slate-50"
                  onError={e => { e.target.src = preview }}
                />
              ) : (
                <div className="h-48 bg-slate-50 rounded-lg flex items-center justify-center text-slate-400 text-sm">
                  No annotated image
                </div>
              )}
            </div>

            {/* Detections table */}
            <div className="card overflow-hidden">
              <div className="px-5 py-3 border-b border-slate-100">
                <h3 className="text-sm font-semibold text-slate-700">
                  Detected Pathologies ({detection.total_defects})
                </h3>
              </div>
              <div className="overflow-y-auto max-h-72">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 sticky top-0">
                    <tr>
                      {['#', 'Defect', 'Confidence', 'Severity'].map(h => (
                        <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-slate-500">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {detection.detections?.map((d, i) => (
                      <tr key={i} className="hover:bg-slate-50/50">
                        <td className="px-3 py-2 text-slate-400 text-xs">{i + 1}</td>
                        <td className="px-3 py-2 font-medium text-slate-700 capitalize">
                          {d.class.replace(/_/g, ' ')}
                        </td>
                        <td className="px-3 py-2 font-mono text-xs text-slate-600">
                          {(d.confidence * 100).toFixed(1)}%
                        </td>
                        <td className="px-3 py-2">
                          <span className={`badge badge-${d.severity?.toLowerCase()}`}>{d.severity}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Report generation */}
          <div className="card p-6">
            <h3 className="text-base font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <FileText size={17} className="text-brand-600" /> Generate AI Report
            </h3>

            <div className="mb-4">
              <label className="label">Engineer Notes (optional)</label>
              <textarea
                value={engineerNotes}
                onChange={e => setNotes(e.target.value)}
                placeholder="Add any observations, site conditions, or context for the AI report…"
                rows={3}
                className="input resize-none"
              />
            </div>

            {!reportResult ? (
              <button onClick={handleReport} disabled={loading} className="btn-primary">
                {loading
                  ? <><Loader2 size={15} className="animate-spin" /> Generating…</>
                  : <><Wand2 size={15} /> Generate AI Report</>}
              </button>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm">
                  <CheckCircle size={15} /> Report generated successfully
                </div>

                {/* Report preview */}
                <div className="bg-slate-50 rounded-lg p-4 space-y-3 text-sm max-h-80 overflow-y-auto">
                  {[
                    ['Executive Summary', 'executive_summary'],
                    ['Recommended Actions', 'recommended_actions'],
                    ['Priority Level', 'priority_level'],
                  ].map(([label, key]) => (
                    <div key={key}>
                      <div className="font-semibold text-slate-700 text-xs uppercase tracking-wide mb-1">{label}</div>
                      <p className="text-slate-600 leading-relaxed">{reportResult.ai_report?.[key] || '—'}</p>
                    </div>
                  ))}
                </div>

                {/* Download buttons */}
                <div className="flex flex-wrap gap-3">
                  <a
                    href={`${API_BASE}${reportResult.docx_url}`}
                    download
                    className="btn-primary"
                    target="_blank" rel="noreferrer"
                  >
                    <Download size={15} /> Download Word (.docx)
                  </a>
                  <a
                    href={`${API_BASE}${reportResult.pdf_url}`}
                    download
                    className="btn-secondary"
                    target="_blank" rel="noreferrer"
                  >
                    <Download size={15} /> Download PDF
                  </a>
                  <button
                    onClick={() => navigate(`/inspection/${detection.inspection_id}`)}
                    className="btn-secondary"
                  >
                    View Full Report
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Start over */}
          <div className="flex justify-end">
            <button onClick={reset} className="btn-secondary">
              <RefreshCw size={15} /> New Inspection
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
