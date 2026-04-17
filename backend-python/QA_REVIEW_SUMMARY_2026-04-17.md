# QA Review Summary - 2026-04-17

## What I ran
- Backend smoke test across auth, recipes, recommend, saved, my-recipes, and feedback.
- Frontend production build smoke.
- Duplicate-visibility check with and without `include_duplicates`.
- Three passes of automated recipe QA candidate extraction.

## Important result
The automated QA heuristics are not reliable enough to auto-fix the dataset safely.

Reason:
- `tags` are stored as JSON arrays.
- Some labels are broad or intentionally coarse (`non-veg`, `vegan`, `dairy_free`, `halal`).
- Substring-based checks produced many false positives.
- Even after parsing JSON tags, a large part of the apparent issue set is caused by classification conventions rather than obvious data corruption.

## Useful artifacts created
- `QA_REVIEW_CANDIDATES_2026-04-17.csv`
- `QA_REVIEW_CANDIDATES_STRICT_2026-04-17.csv`
- `QA_REVIEW_CANDIDATES_FINAL_2026-04-17.csv`

## Best takeaways
- Backend is stable and passed smoke validation.
- Frontend builds successfully.
- Duplicate suppression works by default and can be re-enabled with `include_duplicates=true`.
- The next useful cleanup step should be a small manual review sample, not a bulk auto-correction.

## Recommended next move
- Review the top ~50 rows from `QA_REVIEW_CANDIDATES_FINAL_2026-04-17.csv` manually.
- If needed, tighten classification rules in the enrichment script before any further mass changes.
