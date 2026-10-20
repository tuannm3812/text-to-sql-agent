"""Retrieval metrics over a suite's gold tables: recall@k, full coverage@k and MRR.

The run harness records one number per case, `schema_recall`, for the tables a run sent.
That cannot say whether a missed table ranked seventh or last, or whether a larger `top_k`
would have reached it. These metrics read the full ranking (`rag.rank_schema_chunks`), so
they measure the scorer itself, before foreign-key neighbours are added, and need no model.

For one case with gold tables G and a ranking r_1, r_2, ...:

- **recall@k** is |G ∩ {r_1..r_k}| / |G|;
- **coverage@k** is 1 when every gold table is in the first k, else 0;
- **reciprocal rank** is 1 / (rank of the first gold table), 0 when none is ranked.

Each is averaged over the cases that list gold tables. Table names compare lowercased, as
`runner._schema_recall` compares them.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

DEFAULT_KS: tuple[int, ...] = (1, 2, 3, 4, 6, 8, 10)


@dataclass(frozen=True)
class CaseRanks:
    """Where each gold table of one case ranks; `None` for a gold table not ranked at all."""

    case_id: str
    ranks: Mapping[str, int | None]

    def recall_at(self, k: int) -> float:
        """Share of gold tables in the first `k`."""
        return sum(1 for rank in self.ranks.values() if rank is not None and rank <= k) / len(
            self.ranks
        )

    def covered_at(self, k: int) -> bool:
        """Whether every gold table is in the first `k`."""
        return all(rank is not None and rank <= k for rank in self.ranks.values())

    @property
    def reciprocal_rank(self) -> float:
        """1 / rank of the best-ranked gold table, 0 when none is ranked."""
        ranked = [rank for rank in self.ranks.values() if rank is not None]
        return 1 / min(ranked) if ranked else 0.0

    @property
    def worst_rank(self) -> int | None:
        """Rank of the last gold table, the `k` that covers the case; `None` if one is unranked."""
        ranks = list(self.ranks.values())
        return None if any(rank is None for rank in ranks) else max(r for r in ranks if r)


def case_ranks(case_id: str, ranking: Sequence[str], gold: Iterable[str]) -> CaseRanks | None:
    """`CaseRanks` for one case, or `None` when it lists no gold tables.

    Args:
        case_id: The case's id.
        ranking: Table names, best first (`SchemaChunk.qualified_name` of the ranking).
        gold: The case's `expected_tables`.
    """
    expected = sorted({table.lower() for table in gold})
    if not expected:
        return None
    position: dict[str, int] = {}
    for rank, table in enumerate(ranking, start=1):
        position.setdefault(table.lower(), rank)
    return CaseRanks(case_id, {table: position.get(table) for table in expected})


@dataclass(frozen=True)
class RetrievalSummary:
    """Means over a set of cases with gold tables."""

    cases: int
    recall: Mapping[int, float]
    coverage: Mapping[int, float]
    mrr: float


def summarise(ranks: Sequence[CaseRanks], ks: Sequence[int] = DEFAULT_KS) -> RetrievalSummary:
    """Mean recall@k, coverage@k and MRR over `ranks`; all 0 for an empty set."""
    n = len(ranks)
    if n == 0:
        return RetrievalSummary(0, dict.fromkeys(ks, 0.0), dict.fromkeys(ks, 0.0), 0.0)
    return RetrievalSummary(
        cases=n,
        recall={k: sum(r.recall_at(k) for r in ranks) / n for k in ks},
        coverage={k: sum(r.covered_at(k) for r in ranks) / n for k in ks},
        mrr=sum(r.reciprocal_rank for r in ranks) / n,
    )
