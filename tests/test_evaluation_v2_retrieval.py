"""evaluation_v2.retrieval: recall@k, coverage@k and MRR on hand-written rankings."""

from __future__ import annotations

import pytest

from text_to_sql_agent.evaluation_v2.retrieval import case_ranks, summarise


def test_ranks_are_one_based_lowercased_and_none_when_unranked() -> None:
    ranks = case_ranks("1", ["Orders", "customers", "items"], ["CUSTOMERS", "orders", "gone"])
    assert ranks is not None
    assert dict(ranks.ranks) == {"customers": 2, "gone": None, "orders": 1}


def test_a_case_without_gold_tables_is_left_out() -> None:
    assert case_ranks("1", ["a"], []) is None


def test_recall_coverage_and_reciprocal_rank_of_one_case() -> None:
    ranks = case_ranks("1", ["x", "a", "y", "b"], ["a", "b"])
    assert ranks is not None
    assert [ranks.recall_at(k) for k in (1, 2, 3, 4)] == [0.0, 0.5, 0.5, 1.0]
    assert [ranks.covered_at(k) for k in (2, 4)] == [False, True]
    assert ranks.reciprocal_rank == 0.5
    assert ranks.worst_rank == 4


def test_summary_averages_over_cases() -> None:
    first = case_ranks("1", ["a", "b"], ["a"])
    second = case_ranks("2", ["b", "a"], ["a", "c"])
    assert first is not None and second is not None
    summary = summarise([first, second], ks=(1, 2))
    assert summary.cases == 2
    assert summary.recall == {1: pytest.approx(0.5), 2: pytest.approx(0.75)}
    assert summary.coverage == {1: 0.5, 2: 0.5}
    assert summary.mrr == pytest.approx((1 + 0.5) / 2)
    assert second.worst_rank is None


def test_an_empty_set_summarises_to_zeros() -> None:
    summary = summarise([], ks=(1,))
    assert (summary.cases, summary.recall, summary.mrr) == (0, {1: 0.0}, 0.0)
