## Week 7 — Issue selection

**Issue link:** [Issue #13](https://github.com/ascherj/pathreview/issues/13)

**Issue title:** "Add a content hash to detect unchanged documents and skip re-embedding"

**Tier:** This is a **Tier 2** issue. I am comfortably with this tier because:
* I understand the issue (read Problem summary).
* I have contributed to large codebases before.
* I was able to find the relevant code (e.g., `ingestion/pipeline.py`).
* I understand the surrounding code well enough to change it safely.
* I have read the relevant test files in `tests/unit/`.
* I have estimated the time this will take, and I'm confident I can complete it before the Week 9 deadline.
* The issue has no open blockers or dependencies on other unresolved issues.

**Problem summary:**
When a user re-submits the same README file without, the pipeline does not detect if the content hasn't changed
and re-embeds the document. What is missing is a check that detects if the content hash has changed, and if it
hasn't it skips the embedding step. Fixing this would help reducing unnecessary embedding of unchanged READMEs, which
translates to reducing unnecessary API calls. This issue affects directly the ingestion pipeline logic in `ingestion/pipeline.py`.

**Branch name:** `fix/13-add-content-hash-to-detect-unchanged-docs`

**Setup confirmation:** [✅] App runs locally at localhost:5173

**Cohort ledger:** [✅] Issue added to cohort ledger

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** [Commit fb21f2a
](https://github.com/JoseLoarca/pathreview/commit/fb21f2afd7318f382f4e99f6c77de25680b0f0a2)

**Reproduction summary:**
I wrote a unit tests that verify if the `ingest_readme` function that is part of the `IngestionPipeline` embeds unchanged 
READMEs more than once. I observed that the logic in the pipeline is not fully implemented: the functions that record 
and check for ingested sources have placeholder code.

**PLAN.md link:** [PLAN.md](https://github.com/JoseLoarca/pathreview/blob/fix/13-add-content-hash-to-detect-unchanged-docs/PLAN.md)

**Blockers or open questions:** -

## Week 9 — Solution building & PR submission

### Check-in 1 (Wed 29 Jul)

**Current progress:** I have implemented all the subtasks listed in PLAN.md: fix `_check_skip`, 
fix `_record_ingested_source`, update calls, add unit tests.

**Next steps:** My next steps are to self-review against contribution standards, open a draft PR, and finalize and 
submit the PR.

**Blockers:** -

---

### Check-in 2 (end of week)

**PR link:** [fix(ingestion): skip re-embedding unchanged documents via content hash - #507
](https://github.com/ascherj/pathreview/pull/507)

**Branch:** `fix/13-add-content-hash-to-detect-unchanged-docs`

**What you built:**
This PR fixes unchanged READMEs (and resumes/repo metadata) being needlessly re-embedded on every re-submission by 
wiring up the content-hash deduplication that was already half-built but never functional. _hash_content already 
computed a SHA256 hash, but _check_skip used a broken, always-failing DB query and _record_ingested_source never 
actually persisted anything, so the "already ingested" check silently no-op'd and every ingestion re-ran the embedding 
pipeline regardless of content. Both methods now query/write real IngestedSource rows (keyed by profile_id, source_type, 
and filename, with content_hash compared against the most recent record), and 
ingest_resume/ingest_readme/ingest_repo_metadata were converted to async to match the app's async-only DB session and 
updated to call the fixed methods correctly — eliminating wasted embedding-provider API calls for content that hasn't 
changed.

**Tests added or updated:**
- tests/unit/test_ingestion_pipeline_dedup.py (new) — covers the shared dedup helpers directly:
  - _check_skip returns None when no prior IngestedSource exists for the profile/type/filename.
  - _check_skip returns a skipped IngestResult when the stored content_hash matches the incoming one.
  - _check_skip returns None (proceeds with ingestion) when the stored hash differs from the incoming one.
  - _record_ingested_source builds and persists (add + commit) an IngestedSource row with the correct profile_id, source_type, content_hash, source_url, and chunk_count.
- tests/unit/test_readme_unchanged_detection.py (new) — covers the end-to-end black-box behavior through the public ingest_readme API:
  - Re-submitting the exact same README content is skipped on the second call.
  - Re-submitting unchanged README content only triggers the embedding batch processor once, not on every call.

**Self-review confirmation:** [✅] make check passes  [✅] make test-unit passes - both checks pass with pre-existing failures that are unrelated to this fix

**Draft PR feedback received from:** none