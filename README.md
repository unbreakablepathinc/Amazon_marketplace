# Amazon.de Keyword Cluster Analysis

## Overview

This project evaluates product visibility on **Amazon.de** for the seed keyword **`dessertgläser`**.  
It retrieves search-result data through the Oxylabs Web Scraper API, generates a semantic keyword cluster, and calculates ASIN-level visibility metrics across cluster queries.

## Objectives

- Build a thematic cluster of the **30 most frequent related terms** extracted from search result titles.
- Compute **proportional keyword weights** based on term frequency.
- Measure cross-keyword product visibility for each ASIN:
  - Number of cluster keywords where the ASIN appears
  - Total appearance count across cluster result pages
  - Average ranking position
  - Co-occurrence frequency with at least one **KONZEPT** product on the same results page

## Scope and Methodology

- **Data source:** Amazon.de search result pages
- **Collection method:** Oxylabs Web Scraper API
- **Scope limitation:** Product detail pages are intentionally excluded from analysis

## Technology Stack

- **Backend:** FastAPI, Oxylabs client, Gemini API (required for semantic clustering)
- **Frontend:** Next.js 14 (App Router), React

## Prerequisites

- Python 3.10+ (recommended)
- Node.js 18+ and npm
- Valid Oxylabs credentials
- Gemini API key

## Installation and Run Guide

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OXYLABS_USER=your_user
OXYLABS_PASSWORD=your_password
GEMINI_API_KEY=your_api_key
```

Start the API server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

## Output Schema

| Field | Description |
| --- | --- |
| ASIN | Amazon Standard Identification Number |
| Image | Product image URL from search results |
| Price | Price in EUR, when available |
| Cluster keywords present | Number of cluster keywords whose result pages include this ASIN |
| Frequency in cluster results | Total ASIN occurrences across all cluster keyword result pages |
| Average position | Mean ranking position (1-based) across all occurrences |
| Frequency near KONZEPT | Number of pages where this ASIN appears together with at least one KONZEPT product |

## Notes

- Ranking and visibility metrics depend on live marketplace conditions and may vary over time.
- Data completeness is subject to scraper/API response quality and regional result availability.
