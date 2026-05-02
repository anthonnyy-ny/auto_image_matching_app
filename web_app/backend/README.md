# Web backend prototype

Run from the repository root:

```powershell
uvicorn web_app.backend.main:app --reload
```

Minimal API:

- `GET /health`
- `POST /api/projects`
- `POST /api/projects/{project_id}/images`
- `POST /api/projects/{project_id}/match`
- `GET /api/projects/{project_id}/results`
