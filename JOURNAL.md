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

**Reproduction commit link:** [link to commit documenting the reproduced issue]

**Reproduction summary:**
I wrote a unit tests that verify if the `ingest_readme` function that is part of the `IngestionPipeline` embeds unchanged 
READMEs more than once. I observed that the logic in the pipeline is not fully implemented: the functions that record 
and check for ingested sources have placeholder code.

**PLAN.md link:** [link to PLAN.md in your fork]

**Blockers or open questions:** -