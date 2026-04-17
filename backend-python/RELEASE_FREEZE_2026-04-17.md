# Release Freeze - 2026-04-17

## Snapshot
- Indian-enriched recipe corpus active in `backend-python/recipes.db`
- Recommendation engine warmed and configurable via environment variables
- Duplicate suppression is enabled by default in recipe listings
- Frontend build verified successfully

## Verified Items
- Backend smoke test: pass
- Frontend production build: pass
- Recommendation latency: improved from cold-start ~19s to low single-digit seconds on first request, then ~1.4s steady-state in local validation
- Fallback recommendations now broaden gracefully when strict ingredient overlap returns no results
- UI now surfaces enriched recipe metadata (`variant_type`, `cooking_method`, `protein_type`, `base_recipe`)

## Controls
- `RECOMMENDER_WARMUP_ON_STARTUP=1|0`
- `RECOMMENDER_WARMUP_BATCH_SIZE=<int>`

## Notes
- Candidate QA lists were generated, but automated heuristics were too noisy for safe bulk correction.
- The current release should be treated as a stable baseline unless a targeted QA cleanup pass is approved.
