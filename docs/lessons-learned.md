# Lessons Learned

## 429 quota errors on bulk embedding

**Problem:** `ingest_pdf()`'s `vectorstore.add_documents(chunks)` embeds all chunks
in one burst. Gemini free-tier caps at 100 embed requests/minute. Any PDF producing
>100 chunks hits `RESOURCE_EXHAUSTED`, and the call fails atomically — even chunks
that succeeded before the limit don't get stored.

**Fix:** Batch chunks into groups of 90, `time.sleep(60)` between batches.

```python
BATCH_SIZE = 90
for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i : i + BATCH_SIZE]
    vectorstore.add_documents(batch)
    if i + BATCH_SIZE < len(chunks):
        time.sleep(60)
```

---

## Postgres NUMERIC/Decimal → blank matplotlib charts

**Problem:** Columns typed `NUMERIC` in Postgres come back as Python `Decimal`
objects. Matplotlib doesn't error on this — it silently renders zero-height/blank
bars instead.

**Fix:** Cast to float before plotting: `df[col] = df[col].astype(float)`.

---

## Redundant `search_documents` retries

**Problem:** Agent was firing 2-3 tool calls per question, re-querying with
rephrased versions of the same question (e.g. "gift policy" → "Gift, Hospitality
and Charitable Donations Policy gifts"). Debug prints showed both calls returning
near-identical chunks, just reordered — no retrieval gain, just wasted embedding
calls and latency.

**Root cause:** `k=4` wasn't returning enough chunks to satisfy the model in one
pass on broader questions.

**Fix:** Increased `k` by 2 in `similarity_search()`. Confirmed via repeated testing —
single tool call across varied phrasings/topics post-fix, same answer quality.
Compound questions (e.g. asking about both reporting channels AND retaliation
protection) still legitimately trigger 2 calls — that's correct behavior, not the bug.