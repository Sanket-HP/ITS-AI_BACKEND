# Intent-to-System AI (ITS-AI) – Backend

**Version:** v2.5.0-Visual  
**Status:** Beta (Visual Architecture, XAI, PDF Export)  
**Author:** Sanket Patil  
**Repository:** https://github.com/Sanket-HP/ITS-AI_BACKEND  

---

## 🚀 Overview

**Intent-to-System AI** is an advanced AI-powered backend platform that transforms **high-level human system intent** into a **complete, explainable, and optimized system architecture**.

The system decomposes intent into:
- Structured requirements
- Modular system architectures
- Data flow & decision logic
- Failure simulations
- Optimized designs
- Explainable AI (XAI) justifications
- Visual system graphs
- Exportable JSON & PDF reports

This backend powers the **v2.5.0 Visual Frontend**, supporting real-time architectural reasoning.

---

## 🧠 Core Capabilities

### 1️⃣ Intent Analysis
- Converts natural language intent into:
  - Goals
  - Constraints
  - Actors
  - Success metrics

### 2️⃣ System Architecture Generation
- Modular, production-grade architectures
- Clear responsibilities & data flows
- Decision rules with:
  - Confidence scores
  - Risk levels

### 3️⃣ Failure Simulation
- Best-case / worst-case analysis
- Failure points with:
  - Impact
  - Affected modules
  - Mitigation strategies
- Overall system risk assessment

### 4️⃣ System Optimization
- Optimizes architecture based on objectives:
  - Resilience
  - Cost
  - Speed
  - Fairness
- Produces optimized architecture + tradeoffs

### 5️⃣ Explainable AI (XAI)
- Executive-level explanations
- Every major decision includes:
  - Justification
  - Confidence (%)
  - Risk level (LOW / MEDIUM / HIGH)

### 6️⃣ Visual System Graphs
- Backend-ready graph models (nodes & edges)
- Frontend renders:
  - Mermaid diagrams
  - Architecture flows

### 7️⃣ Export & Reporting
- Full system report aggregation
- JSON export
- PDF report generation (frontend-driven)

---

## 🏗️ Tech Stack

| Layer | Technology |
|-----|-----------|
| Backend Framework | FastAPI |
| Language | Python 3.10+ |
| AI Engine | Google Gemini (Pro) |
| Data Models | Pydantic |
| API Spec | OpenAPI (Swagger) |
| Architecture Style | Modular / Service-Oriented |

---

## 📂 Project Structure

ITS-AI-BACKEND/
│
├── app/
│ ├── api/
│ │ └── routes.py
│ ├── models/
│ │ └── schemas.py
│ ├── services/
│ │ └── gemini_service.py
│ ├── utils/
│ │ └── graph_builder.py
│ └── main.py
│
├── requirements.txt
├── .gitignore
├── README.md
└── .env (not committed)


---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|-------|-------|------------|
| `/api/analyze-intent` | POST | Analyze natural language intent |
| `/api/generate-system` | POST | Generate system architecture |
| `/api/simulate-failure` | POST | Simulate failures & risks |
| `/api/optimize-system` | POST | Optimize architecture |
| `/api/explain-system` | POST | Explain decisions (XAI) |

Swagger UI available at:
[Fast API](http://127.0.0.1:8000/docs)


---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Sanket-HP/ITS-AI_BACKEND.git
cd ITS-AI_BACKEND


 2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Environment variables

Create .env file:

GEMINI_API_KEY=your_api_key_here

5️⃣ Run the server
uvicorn app.main:app --reload