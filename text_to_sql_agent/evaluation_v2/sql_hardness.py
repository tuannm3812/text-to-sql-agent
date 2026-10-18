"""Spider's hardness rule applied to SQL text, for suites that ship no parsed query.

``spider_hardness`` reproduces Spider's official classifier over ``dev.json``'s parsed
``sql`` field. BIRD train ships raw SQL only, so this module counts the same components
from a ``sqlglot`` parse of the text: ``component1`` (WHERE, GROUP BY, ORDER BY, LIMIT,
joins, ``OR``, ``LIKE``), ``component2`` (subqueries in conditions and set operations) and
``others`` (more than one aggregate, output column, WHERE condition or GROUP BY column), then
applies the official thresholds through ``hardness_from_counts``.

It is an approximation of a parser-bound rule, not the rule. Two of the original's quirks
are reproduced on purpose, because they move labels on real queries: a ``NOT`` condition in
WHERE or HAVING counts as an aggregate, and each ``AND``/``OR`` between HAVING conditions
counts as one too. The parse differs where Spider's grammar is flat and SQL is not: a
parenthesised ``(a OR b) AND c`` is counted as the three flat conditions Spider's parser
would produce. Checked on 2026-10-18 against the official labels of all 1,034 Spider dev
queries: every label agrees (``tests/test_evaluation_v2_sql_hardness.py`` repeats the check
whenever the Spider data is present).
"""

from __future__ import annotations

from typing import Any

import sqlglot
from sqlglot import exp

from text_to_sql_agent.evaluation_v2.contract import Hardness
from text_to_sql_agent.evaluation_v2.spider_hardness import hardness_from_counts

_AGG = 1  # any aggregate; spider_hardness only tests "is it 'none'"
_NONE = 0


def _conditions(node: exp.Expression | None) -> tuple[list[exp.Expression], list[str]]:
    """A flat ``[cond, 'and', cond, ...]`` split into its conditions and its connectives."""
    if node is None:
        return [], []
    conditions: list[exp.Expression] = []
    tokens: list[str] = []

    def walk(expression: exp.Expression) -> None:
        if isinstance(expression, exp.Paren):
            walk(expression.this)
        elif isinstance(expression, (exp.And, exp.Or)):
            walk(expression.left)
            tokens.append("or" if isinstance(expression, exp.Or) else "and")
            walk(expression.right)
        else:
            conditions.append(expression)

    walk(node)
    return conditions, tokens


def _is_not(condition: exp.Expression) -> bool:
    return isinstance(condition, exp.Not) or (
        isinstance(condition, exp.In) and bool(condition.args.get("not"))
    )


def _is_like(condition: exp.Expression) -> bool:
    inner = condition.this if isinstance(condition, exp.Not) else condition
    return isinstance(inner, (exp.Like, exp.ILike))


def _nested_in(condition: exp.Expression) -> int:
    """Subqueries used as a condition's value, as Spider's ``cond_unit[3]``/``[4]`` would be."""
    inner = condition.this if isinstance(condition, exp.Not) else condition
    return sum(
        1
        for child in inner.iter_expressions()
        if isinstance(child, (exp.Subquery, exp.Select, exp.SetOperation))
    )


def _has_agg(expression: exp.Expression | None) -> int:
    if expression is None:
        return _NONE
    if isinstance(expression, exp.Alias):
        expression = expression.this
    return _AGG if isinstance(expression, exp.AggFunc) else _NONE


def _table_units(select: exp.Select) -> int:
    units = 1 if select.args.get("from") is not None else 0
    units += len(select.args.get("joins") or [])
    return units


def _join_conditions(select: exp.Select) -> list[exp.Expression | None]:
    return [join.args.get("on") for join in select.args.get("joins") or []]


def _parsed(sql: str, dialect: str) -> dict[str, Any]:
    """The Spider-shaped counts of the outermost query; set operations nest their right side."""
    tree = sqlglot.parse_one(sql, read=dialect)
    # Spider's parser hangs a whole chain of set operations off the first query as one
    # nested query (`A UNION B EXCEPT C` is A with one nested `B EXCEPT C`), so a chain of
    # any length counts once.
    nested = 0
    while isinstance(tree, exp.SetOperation):
        nested = 1
        tree = tree.left
    if isinstance(tree, exp.Subquery):
        tree = tree.this
    if not isinstance(tree, exp.Select):
        raise ValueError(f"not a SELECT: {sql!r}")
    select = tree

    where_conds, where_tokens = _conditions(select.args.get("where") and select.args["where"].this)
    having_conds, having_tokens = _conditions(
        select.args.get("having") and select.args["having"].this
    )
    from_conds: list[exp.Expression] = []
    from_tokens: list[str] = []
    for on in _join_conditions(select):
        conds, tokens = _conditions(on)
        from_conds += conds
        from_tokens += tokens
    group = select.args.get("group")
    group_by = list(group.expressions) if group is not None else []
    order = select.args.get("order")
    order_by = list(order.expressions) if order is not None else []

    all_conds = from_conds + where_conds + having_conds
    comp1 = (
        (1 if where_conds else 0)
        + (1 if group_by else 0)
        + (1 if order_by else 0)
        + (1 if select.args.get("limit") is not None else 0)
        + max(_table_units(select) - 1, 0)
        + sum(1 for token in from_tokens + where_tokens + having_tokens if token == "or")
        + sum(1 for cond in all_conds if _is_like(cond))
    )
    comp2 = nested + sum(_nested_in(cond) for cond in all_conds)

    agg_count = sum(_has_agg(e) for e in select.expressions)
    agg_count += sum(1 for cond in where_conds if _is_not(cond))  # Spider's not_op quirk
    agg_count += sum(_has_agg(e) for e in group_by)
    agg_count += sum(_has_agg(o.this) for o in order_by)
    # Spider's having quirk: every element of the raw list is tested, connectives included.
    agg_count += sum(1 for cond in having_conds if _is_not(cond)) + len(having_tokens)
    others = (
        (1 if agg_count > 1 else 0)
        + (1 if len(select.expressions) > 1 else 0)
        + (1 if len(where_conds) > 1 else 0)
        + (1 if len(group_by) > 1 else 0)
    )
    return {"comp1": comp1, "comp2": comp2, "others": others}


def sql_hardness(sql: str, *, dialect: str = "sqlite") -> Hardness:
    """Spider's hardness label for raw SQL text; ``ValueError`` when it does not parse."""
    try:
        counts = _parsed(sql, dialect)
    except sqlglot.errors.SqlglotError as exc:
        raise ValueError(f"cannot parse gold SQL for hardness: {exc}") from exc
    return hardness_from_counts(counts["comp1"], counts["comp2"], counts["others"])
