# AI-chef--main (Bridge Mode)

This folder has been cleaned and switched to bridge mode.
The previous Node.js backend/frontend stack was archived for safety.

## Archived Location

- `_archive_20260325/phase2-node-stack`
- `_archive_20260325/backend-scripts`
- `_archive_20260325/frontend-temp`
- `_archive_20260325/inactive-docker`
- `_archive_20260325/lockfiles`

## Active Stack (Python)

Primary backend now lives in:
- `../backend-python`

Run backend:
```powershell
cd ..\backend-python
python -m app.main
```

## Test UI

Use either tester in project root:
- `../api-tester.html`
- `../recipe-ui.html`

If needed, serve from local HTTP server:
```powershell
cd ..
python -m http.server 8080
```
Then open:
- `http://localhost:8080/api-tester.html`
- `http://localhost:8080/recipe-ui.html`

## Notes

- Full safety snapshot is available at:
  `../backups/AI-chef--main_snapshot_20260325_120721/AI-chef--main`
- Nothing was permanently deleted in this phase.
