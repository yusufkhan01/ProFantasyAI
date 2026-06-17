# Deployment guide

ProFantasyAI deploys as two decoupled services:

- **Backend (FastAPI)** -> Render (Docker web service, free plan)
- **Frontend (Vite SPA)** -> Netlify (static hosting, free plan)

All the configuration is already in the repo ([`render.yaml`](../render.yaml),
[`netlify.toml`](../netlify.toml), and the `Dockerfile`s). The steps below take ~10 minutes.

---

## Step 0 - Push the code to GitHub

Render and Netlify build from your GitHub repo, so make sure your latest work is pushed:

```bash
git add -A
git commit -m "Modernise ProFantasyAI: FastAPI + React/TS rebuild"
git push origin main
```

## Step 1 - Backend on Render

1. Create an account at https://render.com and connect your GitHub.
2. Click **New +** -> **Blueprint**, pick this repository. Render detects [`render.yaml`](../render.yaml)
   and proposes the `profantasyai-api` web service (Docker, root dir `backend`, health check `/api/health`).
   - Prefer manual setup? **New +** -> **Web Service** -> select the repo -> set **Root Directory** to
     `backend`, **Runtime** to `Docker`. Render injects `$PORT`; the container already respects it.
3. Click **Apply / Create**. The first build takes a few minutes.
4. Copy the service URL, e.g. `https://profantasyai-api.onrender.com`. Verify it:
   - `https://<api>.onrender.com/api/health` -> `{"status":"ok",...}`
   - `https://<api>.onrender.com/docs` -> Swagger UI

> Leave `ALLOWED_ORIGINS` unset for now; you'll set it in Step 3 once you have the Netlify URL.
> Note: the free plan sleeps after ~15 min idle, so the first request after a nap is slow (cold start).

## Step 2 - Frontend on Netlify

1. Create an account at https://netlify.com and connect GitHub.
2. **Add new site** -> **Import an existing project** -> pick this repository.
   Netlify reads [`netlify.toml`](../netlify.toml) (base `frontend`, build `npm run build`, publish `dist`).
3. Before the first deploy (or in **Site settings -> Environment variables**), add:
   - `VITE_API_BASE_URL` = your Render API URL from Step 1 (e.g. `https://profantasyai-api.onrender.com`)
4. Deploy. Copy the site URL, e.g. `https://profantasyai.netlify.app`.

> Vite inlines env vars **at build time**, so after changing `VITE_API_BASE_URL` you must trigger a
> redeploy (**Deploys -> Trigger deploy -> Clear cache and deploy site**).

## Step 3 - Connect the two (CORS)

1. In Render, open the backend service -> **Environment** -> add/update:
   - `ALLOWED_ORIGINS` = your Netlify URL (comma-separate multiple, no trailing slash),
     e.g. `https://profantasyai.netlify.app`
2. Save; Render redeploys automatically. The frontend can now call the API without CORS errors.

## Step 4 - Wire the live URLs into the project

1. In [`README.md`](../README.md), replace the demo placeholder URLs with your real ones.
2. (Optional) In [`frontend/src/components/Header.tsx`](../frontend/src/components/Header.tsx), update
   `REPO_URL` if you rename the GitHub repository.
3. Commit and push - both services auto-redeploy.

---

## CLI alternative (optional)

**Netlify**

```bash
npm i -g netlify-cli
netlify login
cd frontend
netlify deploy --build --prod   # set VITE_API_BASE_URL in the site env first
```

**Render** is easiest via the dashboard/Blueprint; it also supports an API key + the `render` CLI if you
prefer infrastructure-as-code.

## Troubleshooting

- **CORS error in the browser console** -> `ALLOWED_ORIGINS` on Render must exactly match the frontend
  origin (scheme + host, no trailing slash). Redeploy after changing it.
- **Frontend calls `localhost:8000` in production** -> `VITE_API_BASE_URL` wasn't set at build time;
  set it and redeploy with cache cleared.
- **First request is very slow / 502** -> Render free-plan cold start; retry after ~30s.
- **Mixed content blocked** -> ensure `VITE_API_BASE_URL` uses `https://`.
