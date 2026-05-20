# Price Watch

A price tracking application that monitors product prices across Polish e-commerce sites (Ceneo, Allegro) and provides price history, predictions, and shopping recommendations.

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL
- **Frontend**: Next.js 14 App Router, Tailwind CSS, Recharts, React Hot Toast
- **Scrapers**: httpx + BeautifulSoup4
- **ML**: scikit-learn, statsmodels, pandas, numpy

## Features

- Track product prices from Ceneo, Allegro, and generic e-commerce sites
- Price history charts with 30/60/90 day views
- ML-powered price predictions and trend analysis
- Shopping recommendations (buy/wait/watch)
- Price drop alerts via email
- Anomaly detection for unusual price changes

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database URL
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Docs

Visit `http://localhost:8000/docs` for interactive API documentation.
