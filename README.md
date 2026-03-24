# Amazon.de Cluster – Trial Task

For the **amazon.de** marketplace and main keyword **"dessertgläser"**, this project for getting product info:

1. **Builds a thematic cluster** of the 30 most frequently occurring related words, extracted **only from search result titles** (no product detail page crawling).
2. **Computes proportional weight** per keyword (e.g. Dessertgläser 20, Dessertbecher 15 → weights by occurrence).
3. **Measures product visibility**: for each product (ASIN) across cluster keyword results:
   - Number of cluster keywords in which it appears
   - Frequency of appearance in cluster results
   - Average position
   - **Frequency of appearance on the same result page as a "KONZEPT" brand product**

Data is retrieved from **Amazon.de via Oxylabs** Web Scraper API.

## Tech stack

- **Backend:** FastAPI, Oxylabs client, **Gemini (required** for semantic keyword cluster)
- **Frontend:** Next.js 14 (App Router), React

## Setup

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

Create `backend/.env` with `OXYLABS_USER`, `OXYLABS_PASSWORD`, and **`GEMINI_API_KEY`** (required for cluster). Then:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

## Result table fields

| Field                        | Description                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------- |
| ASIN                         | Amazon Standard Identification Number                                                                         |
| Image                        | Product image URL from search results                                                                         |
| Price                        | Price (EUR) when available                                                                                    |
| Cluster keywords present     | Count of cluster keywords in whose results this ASIN appeared                                                 |
| Frequency in cluster results | Total number of times this ASIN appeared across all cluster keyword result pages                              |
| Average position             | Mean position (1-based) across those appearances                                                              |
| Frequency near KONZEPT       | Number of times this product appeared on a result page that also contained at least one KONZEPT brand product |
