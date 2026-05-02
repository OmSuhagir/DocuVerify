**Deploying Backend (Render) & Frontend (Vercel)**

- **Backend (Render)**
  - Push repo to GitHub (already done).
  - On Render create a new **Web Service** and connect your GitHub repo.
  - Set the **Root Directory** to `backend` (so Render installs `backend/requirements.txt`).
  - Build command: `pip install -r requirements.txt` (render.yaml/Procfile already provided).
  - Start command: `gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT` (already in `Procfile`).
  - Environment variables to set on Render:
    - `FASTAPI_ALLOWED_ORIGINS` — comma-separated allowed origins (e.g. `https://your-project.vercel.app`) or `*` to allow all during testing.
    - Render provides `PORT` automatically; do not set it manually.

- **Frontend (Vercel)**
  - On Vercel create a new project from the same GitHub repo and set the **Root Directory** to `frontend`.
  - Framework preset: `Vite` (Vercel usually detects automatically).
  - Build command: `npm run build` and Output Directory: `dist`.
  - Environment variables to set on Vercel:
    - `VITE_API_BASE_URL` — set to your backend URL, e.g. `https://docuverify-backend.onrender.com` (no trailing `/api`).
  - After deployment, Vercel will build and serve the frontend. The frontend reads `VITE_API_BASE_URL` to call the API.

- **Notes & Local testing**
  - Locally the frontend defaults to `'/api'` for dev setups. If running frontend and backend separately, set `VITE_API_BASE_URL` to `http://localhost:8000` in `.env` in `frontend`.
  - Backend CORS is configured via `FASTAPI_ALLOWED_ORIGINS` (comma-separated).
