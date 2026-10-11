"""A paired comparison of two runs that differ in exactly one deliberate setting.

The regression gate (``gates.regression_gate``) refuses any pair whose identities differ in
more than the code under test and the prompt, and it must: a gate over two different
measurements would pass or fail on the difference itself. A controlled experiment - RAG on
against off (gate G8), thinking off against the model's default, evidence on against off - is
exactly such a pair, made on purpose. ``compare_runs`` measures it instead of judging it:

1. Both runs are loaded with the gate's own checks (``gates.load_run``): readable files, status
   ``complete``, row count against the manifest, every ``generation_failure`` cell one the
   runner writes, no repeated id. An uncitable run is loaded, not refused, and the output says
   why it is not citable.
2. The runs must differ in exactly one *factor*, one of ``FACTORS``, among the fields the gate
   checks (``gates.compatible``: the identity minus ``FREE_TO_DIFFER``, plus ``mode``). No
   difference is a regression question; two, or one outside ``FACTORS``, is no controlled
   comparison. ``commit``, ``dirty`` and ``prompt_sha256`` may still differ, and are shown.
3. Cases align by id exactly as the gate aligns them (``gates.aligned_ids``), in the same
   order, so the paired EX interval here and the gate's agree.

Per-run EX and safety cells are the report's own (``report.ex_cell``, ``report.safety_cell``)
over the rows in ``cases.csv`` order, so they equal each run's ``report.md``. Paired changes
use the harness's bootstrap: 10,000 resamples, seed 0. ``render_comparison`` is deterministic:
no timestamps, so the same two runs give byte-identical Markdown.
"""

from __future__ import annotations

import statistics
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from text_to_sql_agent.evaluation_v2.gates import (
    FREE_TO_DIFFER,
    RESAMPLES,
    SEED,
    PairedChange,
    RegressionRefused,
    aligned_ids,
    compatible,
    describe_field,
    field_value,
    format_ids,
    load_run,
    paired_change,
)
from text_to_sql_agent.evaluation_v2.identity import IDENTITY_FIELDS
from text_to_sql_agent.evaluation_v2.manifest import Manifest
from text_to_sql_agent.evaluation_v2.report import (
    HARDNESS_ORDER,
    INTERVAL_MEANING,
    NOT_APPLICABLE,
    Row,
    ex_cell,
    safety_cell,
    terminal,
)
from text_to_sql_agent.evaluation_v2.runner import TOKEN_COLUMNS
from text_to_sql_agent.evaluation_v2.scoring import EMPTY_GENERATED_SQL
from text_to_sql_agent.evaluation_v2.stats import Interval, paired_mean_ci

# The settings a controlled comparison may vary, one at a time.
FACTORS: tuple[str, ...] = ("use_rag", "rag_top_k", "evidence", "ollama_think", "model")


class ComparisonRefused(ValueError):
    """The two runs cannot be compared as a one-factor experiment.

    ``differences`` holds ``(field, new value, baseline value)`` for each differing field when
    the refusal is about the factor.
    """

    def __init__(self, message: str, differences: tuple[tuple[str, str, str], ...] = ()) -> None:
        """Keep the message and the per-field ``(field, new, baseline)`` differences."""
        super().__init__(message)
        self.differences = differences


@dataclass(frozen=True)
class RunSide:
    """One run's own figures: provenance, latency, schema recall and failure counts.

    Latency and recall are over the run's terminal rows with a non-blank cell, as
    ``report.md`` computes them; ``None`` when no row has one.
    """

    run_id: str
    commit: str
    citable: bool
    citable_reason: str
    cases: int
    latency_mean: float | None
    latency_median: float | None
    latency_cases: int
    recall_mean: float | None
    recall_cases: int
    empty_sql: int
    generation_failures: int
    outages: int


@dataclass(frozen=True)
class AccuracyRow:
    """One population's paired accuracy: each run's report cell and the change between them.

    ``helped`` is the cases correct only in the new run, ``hurt`` those correct only in the
    baseline, so ``change.interval.point == (helped - hurt) / cases``.
    """

    population: str
    cases: int
    old_cell: str
    new_cell: str
    change: PairedChange
    helped: int
    hurt: int


@dataclass(frozen=True)
class MeanChange:
    """A per-case quantity over the cases both runs reported: each mean and the paired change."""

    cases: int
    old_mean: float
    new_mean: float
    change: Interval

    @property
    def relative_percent(self) -> float | None:
        """``(new - old) / old`` in percent; ``None`` when the baseline mean is zero."""
        if self.old_mean == 0:
            return None
        return (self.new_mean - self.old_mean) / self.old_mean * 100


@dataclass(frozen=True)
class TokenComparison:
    """One token column's comparison; ``change`` is ``None`` and ``note`` says why."""

    column: str
    change: MeanChange | None
    note: str


@dataclass(frozen=True)
class Comparison:
    """Everything ``render_comparison`` prints, computed once.

    ``also_differ`` holds ``(field, new, baseline)`` for each of ``FREE_TO_DIFFER`` that
    differs: allowed, and shown. ``ex`` is ``None`` when no case is answerable (the ``safety``
    suite); ``safety`` is ``None`` when none is non-answerable, or the runs are gold runs.
    """

    factor: str
    new_value: str
    old_value: str
    also_differ: tuple[tuple[str, str, str], ...]
    suite: str
    subset: str
    mode: str
    cases: int
    new: RunSide
    old: RunSide
    ex: AccuracyRow | None
    by_difficulty: tuple[AccuracyRow, ...]
    safety: AccuracyRow | None
    tokens: tuple[TokenComparison, ...]
    latency: MeanChange | None


def _load(directory: Path, label: str) -> tuple[Manifest, dict[str, Row]]:
    try:
        return load_run(directory, label, require_citable=False)
    except RegressionRefused as exc:
        raise ComparisonRefused(str(exc)) from exc


def _factor(new: Manifest, old: Manifest) -> str:
    differing = compatible(new, old)
    differences = tuple(
        (name, field_value(new, name, old), field_value(old, name, new)) for name in differing
    )
    if not differing:
        raise ComparisonRefused(
            "the runs differ in no setting (at most in commit, dirty or prompt_sha256): "
            "that is a regression question, so use --gate regression"
        )
    if len(differing) > 1 or differing[0] not in FACTORS:
        raise ComparisonRefused(
            f"a comparison varies exactly one of {', '.join(FACTORS)}; these runs differ in: "
            + ", ".join(describe_field(name, new, old) for name in differing),
            differences,
        )
    return differing[0]


def _side(manifest: Manifest, rows: Sequence[Row]) -> RunSide:
    done = terminal(rows)
    latencies = [float(r["latency_ms"]) for r in done if r["latency_ms"]]
    recalls = [float(r["schema_recall"]) for r in done if r["schema_recall"]]
    return RunSide(
        run_id=manifest.run_id,
        commit=manifest.identity.commit,
        citable=manifest.citable,
        citable_reason=manifest.citable_reason,
        cases=len(rows),
        latency_mean=statistics.fmean(latencies) if latencies else None,
        latency_median=statistics.median(latencies) if latencies else None,
        latency_cases=len(latencies),
        recall_mean=statistics.fmean(recalls) if recalls else None,
        recall_cases=len(recalls),
        empty_sql=sum(1 for r in rows if r["error"] == EMPTY_GENERATED_SQL),
        generation_failures=sum(1 for r in done if r["generation_failure"]),
        outages=len(rows) - len(done),
    )


def _accuracy(
    population: str,
    ids: list[str],
    new_rows: dict[str, Row],
    old_rows: dict[str, Row],
    cell: Callable[[Sequence[Row]], str],
) -> AccuracyRow | None:
    change = paired_change(ids, new_rows, old_rows)
    if change is None:
        return None
    chosen = set(ids)

    def correct(rows: dict[str, Row], case_id: str) -> bool:
        return rows[case_id]["outcome"] == "correct"

    return AccuracyRow(
        population=population,
        cases=len(ids),
        # In `cases.csv` order, as `report.md` resamples them: the same cell, digit for digit.
        old_cell=cell([row for case_id, row in old_rows.items() if case_id in chosen]),
        new_cell=cell([row for case_id, row in new_rows.items() if case_id in chosen]),
        change=change,
        helped=sum(1 for i in ids if correct(new_rows, i) and not correct(old_rows, i)),
        hurt=sum(1 for i in ids if correct(old_rows, i) and not correct(new_rows, i)),
    )


def _mean_change(pairs: list[tuple[float, float]]) -> MeanChange | None:
    if not pairs:
        return None
    new = [n for n, _ in pairs]
    old = [o for _, o in pairs]
    return MeanChange(
        cases=len(pairs),
        old_mean=statistics.fmean(old),
        new_mean=statistics.fmean(new),
        change=paired_mean_ci(new, old, resamples=RESAMPLES, seed=SEED),
    )


def _has_tokens(rows: dict[str, Row]) -> bool:
    return any(row[column] for row in rows.values() for column in TOKEN_COLUMNS)


def _tokens(
    column: str, ids: list[str], new_rows: dict[str, Row], old_rows: dict[str, Row]
) -> TokenComparison:
    missing = [
        label
        for label, rows in (("baseline", old_rows), ("new", new_rows))
        if not _has_tokens(rows)
    ]
    if missing:
        whose = "neither run has" if len(missing) == 2 else f"the {missing[0]} run has no"
        return TokenComparison(column, None, f"not recorded ({whose} token counts)")
    # Blank is "not reported", never zero: a case counts only when both runs reported it.
    pairs = [
        (float(new_rows[i][column]), float(old_rows[i][column]))
        for i in ids
        if new_rows[i][column] and old_rows[i][column]
    ]
    change = _mean_change(pairs)
    note = "" if change is not None else "not reported by both runs for any case"
    return TokenComparison(column, change, note)


def compare_runs(new_dir: Path, baseline_dir: Path) -> Comparison:
    """Compare ``new_dir`` with ``baseline_dir``, two runs that differ in one of ``FACTORS``.

    Raises:
        ComparisonRefused: A run is unreadable or incomplete, the runs differ in no factor, in
            more than one, or in a setting outside ``FACTORS``, their case ids or ``expected``
            or ``hardness`` disagree, or there is no case to compare.
    """
    new_manifest, new_rows = _load(new_dir, "new")
    old_manifest, old_rows = _load(baseline_dir, "baseline")
    factor = _factor(new_manifest, old_manifest)
    try:
        ids = aligned_ids(new_rows, old_rows)
    except RegressionRefused as exc:
        raise ComparisonRefused(str(exc)) from exc
    if not ids:
        raise ComparisonRefused("both runs are empty: no case to compare")
    disagree = [i for i in ids if new_rows[i]["hardness"] != old_rows[i]["hardness"]]
    if disagree:
        raise ComparisonRefused(
            f"the runs disagree on 'hardness' for {len(disagree)} case(s): {format_ids(disagree)}"
        )

    answerable = [i for i in ids if new_rows[i]["expected"] == "answerable"]
    others = [i for i in ids if new_rows[i]["expected"] != "answerable"]
    hardness = {new_rows[i]["hardness"] for i in answerable}
    levels = [h for h in HARDNESS_ORDER if h in hardness] + sorted(hardness - set(HARDNESS_ORDER))
    by_difficulty = []
    for level in levels:
        subset = [i for i in answerable if new_rows[i]["hardness"] == level]
        row = _accuracy(level, subset, new_rows, old_rows, ex_cell)
        if row is not None:
            by_difficulty.append(row)

    also_differ = tuple(
        (
            name,
            field_value(new_manifest, name, old_manifest),
            field_value(old_manifest, name, new_manifest),
        )
        for name in IDENTITY_FIELDS
        if name in FREE_TO_DIFFER
        and getattr(new_manifest.identity, name) != getattr(old_manifest.identity, name)
    )
    latency_pairs = [
        (float(new_rows[i]["latency_ms"]), float(old_rows[i]["latency_ms"]))
        for i in ids
        if new_rows[i]["latency_ms"] and old_rows[i]["latency_ms"]
    ]
    return Comparison(
        factor=factor,
        new_value=field_value(new_manifest, factor, old_manifest),
        old_value=field_value(old_manifest, factor, new_manifest),
        also_differ=also_differ,
        suite=new_manifest.identity.suite,
        subset=new_manifest.identity.subset,
        mode=new_manifest.mode,
        cases=len(ids),
        new=_side(new_manifest, list(new_rows.values())),
        old=_side(old_manifest, list(old_rows.values())),
        ex=_accuracy("overall", answerable, new_rows, old_rows, ex_cell),
        by_difficulty=tuple(by_difficulty),
        # A gold run scores no non-answerable case, as in the regression gate.
        safety=(
            None
            if new_manifest.mode == "gold"
            else _accuracy("overall", others, new_rows, old_rows, safety_cell)
        ),
        tokens=tuple(_tokens(column, ids, new_rows, old_rows) for column in TOKEN_COLUMNS),
        latency=_mean_change(latency_pairs),
    )


# --- rendering -----------------------------------------------------------------------------


def _signed(value: float, digits: int = 1) -> str:
    """``value`` with an explicit sign; a value that rounds to zero is ``+0.0``, never ``-0.0``."""
    text = f"{value:+.{digits}f}"
    return "+" + text[1:] if float(text) == 0 else text


def _points(interval: Interval) -> str:
    return (
        f"{_signed(interval.point * 100)} "
        f"[{_signed(interval.low * 100)}, {_signed(interval.high * 100)}]"
    )


def _amount(interval: Interval) -> str:
    return f"{_signed(interval.point)} [{_signed(interval.low)}, {_signed(interval.high)}]"


def _relative(change: MeanChange) -> str:
    relative = change.relative_percent
    return "undefined (baseline mean 0)" if relative is None else f"{_signed(relative)}%"


def _citable(side: RunSide) -> str:
    return "yes" if side.citable else f"no - {side.citable_reason}"


def _accuracy_table(title: str, metric: str, rows: Sequence[AccuracyRow]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        f"| Population | Cases | Baseline {metric} | New {metric} | Paired change (points) "
        "| Helped | Hurt |",
        "|---|---:|---|---|---|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.population} | {row.cases} | {row.old_cell} | {row.new_cell} | "
            f"{_points(row.change.interval)} | {row.helped} | {row.hurt} |"
        )
    return [*lines, ""]


def _tokens_section(tokens: Sequence[TokenComparison]) -> list[str]:
    lines = ["## Cost (tokens per case)", ""]
    measured = [t for t in tokens if t.change is not None]
    if measured:
        lines += [
            "| Tokens | Cases both reported | Baseline mean | New mean "
            "| Paired difference (mean) | Relative change |",
            "|---|---:|---:|---:|---|---:|",
        ]
        for token in measured:
            change = token.change
            assert change is not None
            lines.append(
                f"| {token.column.removesuffix('_tokens')} | {change.cases} | "
                f"{change.old_mean:.1f} | {change.new_mean:.1f} | {_amount(change.change)} | "
                f"{_relative(change)} |"
            )
        lines.append("")
    lines += [
        f"- {token.column.removesuffix('_tokens').capitalize()} tokens: {token.note}."
        for token in tokens
        if token.change is None
    ]
    if len(measured) < len(tokens):
        lines.append("")
    return lines


def _optional(value: float | None, digits: int) -> str:
    return NOT_APPLICABLE if value is None else f"{value:.{digits}f}"


def _latency_section(comparison: Comparison) -> list[str]:
    lines = [
        "## Latency (ms per case)",
        "",
        "| Run | Cases | Mean | Median |",
        "|---|---:|---:|---:|",
    ]
    for label, side in (("Baseline", comparison.old), ("New", comparison.new)):
        lines.append(
            f"| {label} | {side.latency_cases} | {_optional(side.latency_mean, 1)} | "
            f"{_optional(side.latency_median, 1)} |"
        )
    lines.append("")
    change = comparison.latency
    if change is None:
        lines.append("Paired difference: no case was timed in both runs.")
    else:
        lines.append(
            f"Paired difference in mean latency, new minus baseline, over the {change.cases} "
            f"cases both runs timed: {_amount(change.change)} ms ({_relative(change)})."
        )
    return [*lines, ""]


def _other_section(comparison: Comparison) -> list[str]:
    old, new = comparison.old, comparison.new

    def recall(side: RunSide) -> str:
        if side.recall_mean is None:
            return NOT_APPLICABLE
        return f"{side.recall_mean:.3f} (n={side.recall_cases})"

    return [
        "## Other",
        "",
        "| | Baseline | New |",
        "|---|---:|---:|",
        f"| Mean schema recall | {recall(old)} | {recall(new)} |",
        f"| `{EMPTY_GENERATED_SQL}` errors | {old.empty_sql} | {new.empty_sql} |",
        f"| Generation failures | {old.generation_failures} | {new.generation_failures} |",
        f"| Outages | {old.outages} | {new.outages} |",
        "",
    ]


def render_comparison(comparison: Comparison) -> str:
    """The comparison as Markdown. Deterministic: the same inputs give the same bytes."""
    c = comparison
    old, new = c.old, c.new
    lines = [
        f"# `{c.factor}`: {c.old_value} (baseline) vs {c.new_value} (new)",
        "",
        f"- Baseline: `{old.run_id}` at commit `{old.commit}`",
        f"- New: `{new.run_id}` at commit `{new.commit}`",
        "",
        f"Suite `{c.suite}`, subset `{c.subset}`, mode `{c.mode}`: {c.cases} cases, paired by "
        f"id. The runs differ in `{c.factor}` and in no other setting the regression gate "
        "checks.",
        "",
        "| | Baseline | New |",
        "|---|---|---|",
        f"| Citable | {_citable(old)} | {_citable(new)} |",
        f"| Cases | {old.cases} | {new.cases} |",
    ]
    lines += [f"| {name} | `{old_v}` | `{new_v}` |" for name, old_v, new_v in _rows(c)]
    lines.append("")
    if c.also_differ:
        names = ", ".join(f"`{name}`" for name, _, _ in c.also_differ)
        lines += [
            f"Also differing: {names}. The regression gate lets the code under test and the "
            "prompt differ too, so these do not make the pair incompatible; they are part of "
            "what changed between the two runs.",
            "",
        ]
    if c.ex is not None:
        lines += _accuracy_table(
            "Execution accuracy (answerable cases)", "EX", [c.ex, *c.by_difficulty]
        )
    else:
        lines += ["No case is answerable, so EX is not applicable.", ""]
    if c.safety is not None:
        lines += _accuracy_table(
            "Safety accuracy (refusal and unanswerable cases)", "safety", [c.safety]
        )
    lines += _tokens_section(c.tokens)
    lines += _latency_section(c)
    lines += _other_section(c)
    lines += [
        "## How to read this",
        "",
        "Each paired change is new minus baseline, case by case over the cases both runs "
        f"share: a 95 % percentile-bootstrap interval, {RESAMPLES:,} resamples of the cases "
        f"with replacement, each case keeping its pair, seed {SEED}. Cases both runs get right, "
        "or both get wrong, cancel out, which usually makes the interval narrower than the two "
        "runs' separate intervals suggest. Accuracy changes are in percentage points: helped "
        "counts the cases correct only in the new run, hurt those correct only in the "
        "baseline, and the point change is (helped - hurt) / cases. An interval that excludes "
        "zero is a difference larger than resampling the cases explains; one that spans zero "
        "is not. "
        f"{INTERVAL_MEANING}",
        "",
        "Each run's own EX and safety cells are the cells of its `report.md`: "
        "`point [low, high] (k/n)` in percent. Token and latency differences are means over the "
        "cases both runs reported; a blank cell in `cases.csv` is not reported and is never "
        "counted as zero. This is a measurement, not a regression verdict: "
        "`--gate regression` refuses a pair that differs in a setting.",
        "",
    ]
    return "\n".join(lines)


def _rows(comparison: Comparison) -> list[tuple[str, str, str]]:
    """``(field, baseline, new)`` for the factor and every free-to-differ field that differs."""
    rows = [(comparison.factor, comparison.old_value, comparison.new_value)]
    rows += [(name, old_v, new_v) for name, new_v, old_v in comparison.also_differ]
    return rows
