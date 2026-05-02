# Web app

Run the backend from the repository root:

```powershell
uvicorn web_app.backend.main:app --reload
```

Run the frontend from `web_app/frontend`:

```powershell
npm run dev -- --port 5173
```

Open:

- Frontend: http://127.0.0.1:5173
- Backend API docs: http://127.0.0.1:8000/docs

Main API:

- `GET /health`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/projects/{project_id}/images`
- `POST /api/projects/{project_id}/match`
- `POST /api/projects/{project_id}/match/jobs`
- `GET /api/jobs/{job_id}`
- `POST /api/jobs/{job_id}/cancel`
- `GET /api/projects/{project_id}/results`
- `PUT /api/projects/{project_id}/results`
- `GET /api/projects/{project_id}/image`
- `GET /api/projects/{project_id}/project-file`
- `GET /api/projects/{project_id}/export`
- `POST /api/projects/import`
- `POST /api/cache/clear`

The exported ZIP includes grouped images plus `project.json`, `manifest.json`, and `manifest.csv`.
