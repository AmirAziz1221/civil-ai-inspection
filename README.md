# CivilScan AI — Civil Infrastructure Pathology Detection

> AI-powered civil engineering inspection platform for **Dani**  
> Detects pathologies in facades, roads, bridges, PV panels, powerlines, and slopes.

---

## 🏗️ Architecture

```
┌─────────────────────┐     HTTP/REST      ┌──────────────────────────┐
│   React Frontend    │ ◄────────────────► │   FastAPI Backend        │
│   (Port 3000)       │                    │   (Port 8000)            │
│                     │                    │                          │
│  • Dashboard        │                    │  • /upload               │
│  • New Inspection   │                    │  • /detect               │
│  • History          │                    │  • /generate-report      │
│  • Report Viewer    │                    │  • /download/docx/:id    │
└─────────────────────┘                    │  • /download/pdf/:id     │
                                           │  • /inspections          │
                                           └──────────┬───────────────┘
                                                      │
                                    ┌─────────────────┼──────────────┐
                                    │                 │              │
                               YOLO/PyTorch       SQLite         LLM API
                               (.pt models)      Database    (OpenAI/Ollama)
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Your `.pt` model files (optional — demo mode works without them)

### 1. Clone and configure

```bash
git clone <repo-url>
cd civil-ai-inspection

# Copy env template and fill in your values
cp backend/.env.example backend/.env
```

### 2. Add your YOLO models (optional)

Place your `.pt` files in `backend/models/`:

```
backend/models/
├── facade pathologies detection.pt
├── asphalts pathologies detection.pt
├── concreate & bragies pathologies detection.pt
├── PV pathologies detection.pt
├── powerline and towers pathologies detection.pt
└── slopes pathologies detection.pt
```

> **Without model files**: The system runs in **demo mode** — it generates realistic mock detections so you can test the full workflow including report generation.

### 3. Launch

```bash
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ⚙️ LLM Configuration

Edit `backend/.env` to swap LLM providers — no code changes needed:

```env
# OpenAI (default)
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini

# Ollama (local, completely free)
LLM_API_BASE=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3

# Groq (fast, free tier available)
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_...
LLM_MODEL=llama3-70b-8192
```

> **Without an API key**: The system uses a built-in template-based fallback. Reports are still generated with professional civil engineering language — just not AI-customised.

---

## 🔬 Detection Models

| Key | Model File | Asset Type |
|-----|-----------|------------|
| `facade` | `facade pathologies detection.pt` | Building facades |
| `asphalt` | `asphalts pathologies detection.pt` | Roads & pavements |
| `concrete` | `concreate & bragies pathologies detection.pt` | Concrete & bridges |
| `pv` | `PV pathologies detection.pt` | Photovoltaic systems |
| `powerline` | `powerline and towers pathologies detection.pt` | Power infrastructure |
| `slopes` | `slopes pathologies detection.pt` | Slopes & embankments |

---

## 📋 API Reference

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/upload` | Upload image/video |
| `POST` | `/detect` | Run AI detection |
| `POST` | `/generate-report` | Generate Word+PDF report |
| `GET` | `/download/docx/{id}` | Download Word report |
| `GET` | `/download/pdf/{id}` | Download PDF report |
| `GET` | `/inspections` | List all inspections |
| `GET` | `/inspection/{id}` | Get inspection details |
| `GET` | `/models` | List available models |

Full interactive docs: http://localhost:8000/docs

---

## 📁 Project Structure

```
civil-ai-inspection/
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── model_loader.py      # YOLO model registry & loader
│   ├── detection.py         # Inference engine (real + mock)
│   ├── report_generator.py  # Word & PDF report creation
│   ├── llm_client.py        # LLM integration (swap here)
│   ├── database.py          # SQLite CRUD
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── models/              ← Place .pt files here
│   ├── uploads/             ← Uploaded images
│   ├── outputs/             ← Annotated images
│   └── reports/             ← Generated reports
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Router + layout
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── InspectionPage.jsx
│   │   │   ├── HistoryPage.jsx
│   │   │   └── InspectionDetail.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## 🔧 Development (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env: VITE_API_URL=http://localhost:8000
npm run dev
```

---

## 📄 Report Contents

Each generated report includes:

1. **Title Page** — Prepared for Dani
2. **Project Information** — Date, asset type, model, file
3. **Detection Summary** — Total defects, severity breakdown table
4. **Detection Details** — Per-defect class, confidence, severity
5. **Visual Evidence** — Original + annotated images
6. **AI Interpretation** — Professional engineering analysis
7. **Defect Descriptions** — Technical defect characterization
8. **Possible Causes** — Root cause analysis
9. **Severity Assessment** — Engineering justification
10. **Risk Assessment** — Structural integrity implications
11. **Recommended Actions** — Prioritized repair guidance
12. **Priority Level** — Immediate / Short-term / Long-term
13. **Final Conclusion** — Summary and next steps
14. **Disclaimer** — AI verification note

---

## 🛡️ Disclaimer

This tool is for **preliminary inspection support** only. All AI-generated findings must be verified by a qualified, licensed civil engineer before any remediation or safety decisions are made.

---

*CivilScan AI · Prepared for Dani*
