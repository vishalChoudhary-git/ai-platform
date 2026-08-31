# RAG Evaluation Metrics — Interview Additions

## MRR — Mean Reciprocal Rank

**MRR evaluates where the first relevant result appears in the ranked list.**

The score for a query is:

```text
1 ÷ position of the first relevant result
```

Examples:

```text
First relevant result at position 1
→ 1 / 1 = 1.0

First relevant result at position 2
→ 1 / 2 = 0.5

First relevant result at position 5
→ 1 / 5 = 0.2
```

MRR is especially useful when we care about getting **at least one good result very high in the ranking**.

### Interview answer

> "MRR measures how high the first relevant result appears. If the first relevant result is at rank 1, the reciprocal rank is 1; if it is at rank 5, it is 0.2. We average that value across queries."

---

## NDCG — Normalized Discounted Cumulative Gain

**NDCG evaluates the overall quality of the ranking, especially when results have different levels of relevance.**

For example:

```text
3 → highly relevant
2 → relevant
1 → weakly relevant
0 → irrelevant
```

A highly relevant result near the top contributes more than the same result buried near the bottom. Therefore NDCG penalizes a ranking where highly relevant documents appear too low.

### Interview answer

> "NDCG measures the quality of the whole ranking using graded relevance. It gives more importance to highly relevant results appearing near the top and discounts results appearing lower in the list."

### MRR vs NDCG

```text
MRR
→ Where is the FIRST relevant result?

NDCG
→ How good is the OVERALL ranking?
```

In our RAG evaluation, both are useful because MRR tells us whether we surface a useful result early, while NDCG tells us whether the ranking quality across the retrieved candidates is good.
