# 🛡️ Sentinel AI - Version 2.0
**AI-Powered Military Intelligence Decision Support Platform**

Sentinel AI is a professional military intelligence platform that ingests real-world conflict data (Global Terrorism Database & ACLED) and live feeds (GDELT, NewsAPI) to provide predictive threat assessments, deep geographic analytics, and AI-driven intelligence briefings.

## 🚀 Key Features V2.0
- **Multi-Factor Risk Engine:** Combines Machine Learning, FAISS Semantic Similarity, and Regional Statistics to evaluate operational scenarios.
- **Unified Intelligence Database:** Merges GTD and ACLED datasets into a single, clean Parquet pipeline.
- **Live Intelligence Feeds:** GDELT and NewsAPI adapters for real-time situational awareness.
- **Semantic Incident Explorer:** Vector-based search across hundreds of thousands of historical incidents.
- **Intelligence Copilot:** Context-aware LLM copilot for strategic briefings and executive summaries.
- **Executive Report Generator:** Export comprehensive Markdown and PDF intelligence reports.
- **Geographic Intelligence Map:** Clustered, interactive heatmap of global threats.

## 📦 Architecture
- **Backend:** FastAPI, FAISS, Scikit-Learn, SQLAlchemy, SQLite
- **Frontend:** Streamlit, Plotly, Folium
- **Data Pipeline:** Pandas, PyArrow, FastParquet

## ⚙️ Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory based on `.env.example`:
```env
# Core API Settings
API_PORT=8000
ENVIRONMENT=production

# Database & FAISS
DB_PATH=database/sentinel.db
FAISS_INDEX_PATH=rag/index/sentinel.index

# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Live Intelligence APIs (Optional)
GDELT_ENABLED=true
NEWSAPI_ENABLED=true
NEWSAPI_KEY=your_newsapi_key_here
```

### 3. Initialize the V2.0 Data Pipeline
Place your raw dataset files in `datasets/raw/` (e.g. GTD `.xlsx`, ACLED `.csv`), then run the setup script to compile the unified parquet dataset, populate the database, build the FAISS vector index, and train the ML model:
```bash
python setup_data_pipeline.py
```

## 🚀 Running the System

You must start both the backend API and the frontend dashboard.

**Start the Backend (Terminal 1):**
```bash
uvicorn api.main:app --reload
```

**Start the Frontend (Terminal 2):**
```bash
streamlit run frontend/app.py
```

Navigate to `http://localhost:8501` to access the Sentinel AI V2.0 Dashboard.
