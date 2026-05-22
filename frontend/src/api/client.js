import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 300000,
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail || err.message || 'Unknown error'
    return Promise.reject(new Error(message))
  }
)

export const uploadImage = (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress) onProgress(Math.round((e.loaded * 100) / e.total))
    },
  })
}

export const runDetection = (imageId, modelName, assetType) =>
  api.post('/detect', { image_id: imageId, model_name: modelName, asset_type: assetType })

export const generateReport = (inspectionId, engineerNotes) =>
  api.post('/generate-report', { inspection_id: inspectionId, engineer_notes: engineerNotes })

export const getInspections = () => api.get('/inspections')

export const getInspection = (id) => api.get(`/inspection/${id}`)

export const getModels = () => api.get('/models')

export const getDownloadUrl = (type, reportId) => `${BASE_URL}/download/${type}/${reportId}`

export default api
