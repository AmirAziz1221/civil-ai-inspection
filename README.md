# CivilScan AI — Civil Infrastructure Pathology Detection

> AI-powered civil engineering inspection platform  
> **Prepared for: Dani** · Powered by YOLO + Groq LLaMA

[![Live App](https://img.shields.io/badge/Live%20App-civil--ai--inspection.vercel.app-blue?style=for-the-badge)](https://civil-ai-inspection.vercel.app)
[![API Docs](https://img.shields.io/badge/API%20Docs-railway.app-green?style=for-the-badge)](https://civil-ai-inspection-production.up.railway.app/docs)
[![GitHub](https://img.shields.io/badge/GitHub-AmirAziz1221-black?style=for-the-badge&logo=github)](https://github.com/AmirAziz1221/civil-ai-inspection)

---

## 🌐 Live Deployment

| Service | URL |
|---------|-----|
| 🌐 **Frontend (Client App)** | https://civil-ai-inspection.vercel.app |
| ⚙️ **Backend API** | https://civil-ai-inspection-production.up.railway.app |
| 📖 **API Documentation** | https://civil-ai-inspection-production.up.railway.app/docs |

---

## 🎯 What This System Does

Upload a photo of any civil infrastructure and get a **full AI-powered inspection report** in minutes — including annotated images, defect classification, severity levels, and professional PDF/Word reports.

### ✅ Supported Asset Types (5 Models)

| Model | Asset Type | Detects |
|-------|-----------|---------|
| 🏢 **Facade** | Building Facades | Cracks, spalling, efflorescence, corrosion |
| 🛣️ **Asphalt** | Roads & Pavements | Potholes, longitudinal/transverse cracks, rutting |
| 🌉 **Concrete & Bridges** | Concrete Structures | Structural cracks, rebar exposure, deformation |
| ☀️ **PV Panels** | Photovoltaic Systems | Hotspots, micro-cracks, soiling, delamination |
| ⚡ **Powerline & Towers** | Power Infrastructure | Corrosion, broken insulators, wire damage |

---

## 🏗️ Architecture

```
┌─────────────────────┐     HTTP/REST      ┌──────────────────────────┐
│   React Frontend    │ ◄────────────────► │   FastAPI Backend        │
│   Vercel (Free)     │                    │   Railway (Free)         │
│                     │                    │                          │
│  • Dashboard        │                    │  • /upload               │
│  • New Inspection   │                    │  • /detect               │
│  • History          │                    │  • /generate-report      │
│  • Report Viewer    │                    │  • /download/docx/:id    │
└─────────────────────┘                    │  • /download/pdf/:id     │
                                           └──────────┬───────────────┘
                                                      │
                                    ┌─────────────────┼──────────────┐
                                    │                 │              │
                               YOLO/PyTorch       SQLite         Groq LLaMA
                               (.pt models)      Database      (Free API)
```

---

## 📋 How to Use

1. Open **https://civil-ai-inspection.vercel.app**
2. Click **"New Inspection"** in the sidebar
3. **Upload** a photo of your infrastructure (JPG, PNG, BMP)
4. **Select** the matching detection model
5. Click **"Run AI Detection"** — AI analyses the image
6. Add optional **engineer notes**
7. Click **"Generate AI Report"**
8. **Download** your report as Word (.docx) or PDF

---

## 📄 Report Contents

Each generated report includes:

1. **Title Page** — Prepared for Dani
2. **Project Information** — Date, asset type, model, filename
3. **Detection Summary** — Total defects, severity breakdown
4. **Detection Details** — Per-defect class, confidence score, severity
5. **Visual Evidence** — Original + annotated images with bounding boxes
6. **AI Interpretation** — Professional civil engineering analysis
7. **Defect Descriptions** — Technical characterization of each defect
8. **Possible Causes** — Root cause analysis
9. **Severity Assessment** — Engineering justification
10. **Risk Assessment** — Structural integrity implications
11. **Recommended Actions** — Prioritized repair guidance
12. **Priority Level** — Immediate / Short-term / Long-term
13. **Final Conclusion** — Summary and next steps
14. **Disclaimer** — AI verification notice

---

## 📋 API Reference

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/upload` | Upload image/video file |
| `POST` | `/detect` | Run AI detection on uploaded image |
| `POST` | `/generate-report` | Generate Word + PDF report |
| `GET` | `/download/docx/{id}` | Download Word report |
| `GET` | `/download/pdf/{id}` | Download PDF report |
| `GET` | `/inspections` | List all inspections |
| `GET` | `/inspection/{id}` | Get single inspection details |
| `GET` | `/models` | List available detection models |

Full interactive docs: https://civil-ai-inspection-production.up.railway.app/docs

---

## 🚀 Run Locally with Docker

### Prerequisites
- Docker Desktop installed and running
- Git installed

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/AmirAziz1221/civil-ai-inspection.git
cd civil-ai-inspection

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your LLM API key

# 3. Add your .pt model files (optional)
# Place them in backend/models/

# 4. Launch
docker-compose up --build
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## ⚙️ LLM Configuration

Edit `backend/.env` to swap providers — **no code changes needed:**

```env
# Groq (current - fast and free)
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_API_KEY=your-groq-key
LLM_MODEL=llama-3.3-70b-versatile

# OpenAI
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini

# Ollama (local, completely free)
LLM_API_BASE=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3
```

> **Without an API key:** The system uses a built-in professional template fallback — reports still generate correctly.

---

## 📁 Project Structure

```
civil-ai-inspection/
├── backend/
│   ├── main.py              # FastAPI app & all endpoints
│   ├── model_loader.py      # YOLO model registry & loader
│   ├── detection.py         # Inference engine (real + demo mode)
│   ├── report_generator.py  # Word & PDF report generation
│   ├── llm_client.py        # LLM integration (swap provider here)
│   ├── database.py          # SQLite CRUD operations
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── models/              ← Place .pt model files here
│   ├── uploads/             ← Uploaded images stored here
│   ├── outputs/             ← Annotated images stored here
│   └── reports/             ← Generated reports stored here
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Router + sidebar layout
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # Stats + recent inspections
│   │   │   ├── InspectionPage.jsx  # 4-step inspection wizard
│   │   │   ├── HistoryPage.jsx  # Searchable inspection history
│   │   │   └── InspectionDetail.jsx  # Full report viewer
│   │   ├── api/
│   │   │   └── client.js        # Axios API client
│   │   └── index.css            # Tailwind + custom styles
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Tailwind CSS, Vite, Recharts |
| **Backend** | FastAPI, Python 3.11, Uvicorn |
| **AI Models** | Ultralytics YOLO, PyTorch |
| **LLM** | Groq (LLaMA 3.3 70B) — OpenAI-compatible |
| **Database** | SQLite |
| **Reports** | python-docx (Word), ReportLab (PDF) |
| **Image Processing** | OpenCV, Pillow |
| **Deployment** | Docker, Railway (backend), Vercel (frontend) |

---

## 🛡️ Disclaimer

This tool is for **preliminary inspection support only**. All AI-generated findings must be verified and validated by a qualified, licensed civil engineer before any remediation or safety-critical decisions are made.

---

*CivilScan AI v1.0 · Prepared for Dani · Built with ❤️ using YOLO + Groq LLaMA*
