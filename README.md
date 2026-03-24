# Amazon.de Keyword Cluster Analysis

This project analyzes product visibility on **Amazon.de** for the seed keyword **`dessertgläser`**.

Using Amazon search result data (via Oxylabs), it builds a keyword cluster and calculates visibility metrics for products (ASINs) across cluster queries.

## What This Project Does

1. Builds a thematic cluster of the **30 most frequent related terms** found in search result titles.
2. Computes a **proportional weight** for each cluster keyword based on occurrence frequency.
3. Measures product visibility for each ASIN across cluster keyword result pages:
   - Number of cluster keywords where the ASIN appears
   - Total appearance frequency across all cluster results
   - Average search position
   - Frequency of appearing on the same results page as a **KONZEPT** brand product

> Note: Only search result pages are analyzed. Product detail pages are not crawled.

## Data Source

- **Marketplace:** Amazon.de
- **Acquisition method:** Oxylabs Web Scraper API

## Tech Stack

- **Backend:** FastAPI, Oxylabs client, Gemini API (required for semantic clustering)
- **Frontend:** Next.js 14 (App Router), React

## Setup

### 1) Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

Create `backend/.env` with:

- `OXYLABS_USER`
- `OXYLABS_PASSWORD`
- `GEMINI_API_KEY` (required for keyword clustering)

Run the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

## Output Fields

| Field | Description |
| --- | --- |
| ASIN | Amazon Standard Identification Number |
| Image | Product image URL from search results |
| Price | Price (EUR), when available |
| Cluster keywords present | Number of cluster keywords whose result pages include this ASIN |
| Frequency in cluster results | Total occurrences of this ASIN across all cluster keyword result pages |
| Average position | Mean rank position (1-based) across all appearances |
| Frequency near KONZEPT | Number of result pages where this ASIN appears together with at least one KONZEPT brand product |
