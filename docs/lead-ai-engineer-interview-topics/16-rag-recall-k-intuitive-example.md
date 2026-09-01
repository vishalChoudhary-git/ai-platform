# Recall@K — Intuitive Example

## Example: Company Financial Report

Imagine you upload a company financial report to your RAG pipeline.

- There are **5 different chunks** inside your database that contain the answer to: **"What were our Q3 losses?"**
- Therefore, **Total Relevant = 5**.
- A user submits that exact query.
- The retriever fetches the top **4 chunks**, so **K = 4**.
- Out of those 4 fetched chunks, **3 are actually relevant** and **1 is junk/unrelated**.

### Calculation

\[
\text{Recall@4} = \frac{\text{Relevant Retrieved}}{\text{Total Relevant}} = \frac{3}{5} = 0.60 = 60\%
\]

Your retriever achieved a **Recall@4 of 60%**.

### What does that mean intuitively?

The system found **3 of the 5 pieces of relevant information** that existed in the database.

```text
Total relevant chunks in DB

[1] ✅
[2] ✅
[3] ✅
[4] ✅
[5] ✅

Top-4 retrieved

[1] ✅ relevant
[2] ✅ relevant
[6] ❌ junk
[3] ✅ relevant

Relevant retrieved = 3
Total relevant    = 5

Recall@4 = 3 / 5 = 60%
```

To catch more of the remaining relevant information, you would need to increase **K** or improve the retrieval strategy.

### Important interview distinction

Recall@K is about **coverage of relevant information**.

It does **not** tell us whether the retrieved results are clean. For that, metrics such as **Precision@K** are useful.

```text
Recall@K
→ How much of the relevant information did we retrieve?

Precision@K
→ How much of what we retrieved was actually relevant?
```

### RAG interview answer

> "Recall@K measures how many of the known relevant chunks were retrieved within the top K results. For example, if five chunks contain the answer and our top four results contain three of them, Recall@4 is 3 divided by 5, or 60%."
