"""How much of the context window a suite's prompts would take, before any model is called.

    uv run python scripts/report_prompt_sizes.py --suite bird_train_large [--context 32768]

For every case, the three schema contexts the attribution arms send are rendered at HEAD:
plain DDL (RAG off), DDL plus value hints (RAG on, top_k 0) and the shipped top-6 selection.
Each is placed in the user message exactly as `generate_sql` builds it (`llm.build_user_prompt`,
headings and separators included), added to the system prompt, and converted to tokens at
`--chars-per-token`. The default, 1.6, is the lowest ratio the BIRD dev k=0 run measured (its
largest prompt, 12,221 chars, cost 7,488 tokens; the median case was 3.9). That ratio is an
estimate, not a bound: another suite's text can tokenise worse, and the provider's chat
framing and the completion budget also take room. The report, Markdown on stdout, gives each
database's largest prompt per arm and the cases whose estimate exceeds the context window.
It is a planning check for an arm that the provider might truncate silently (Ollama drops
the front of an over-long prompt, which is where the system prompt is), not proof that no
prompt was truncated; the run's recorded prompt tokens are the evidence after the fact.

Read-only; no model is called. Exit 0 always; the numbers are the result.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from text_to_sql_agent.config import DEFAULT_RAG_TOP_K  # noqa: E402 - after the sys.path insert
from text_to_sql_agent.evaluation_v2 import Case, load_suite  # noqa: E402
from text_to_sql_agent.evaluation_v2.runner import (  # noqa: E402
    question_text,
    read_subset_ids,
    resolve_db_path,
)
from text_to_sql_agent.llm import SQL_TRANSLATION_SYSTEM_PROMPT, build_user_prompt  # noqa: E402
from text_to_sql_agent.rag import retrieve_schema_context  # noqa: E402
from text_to_sql_agent.schema import get_schema, get_schema_chunks_and_plain_ddl  # noqa: E402
from text_to_sql_agent.types import render_schema_text  # noqa: E402

ARMS = ("plain_ddl", "ddl_with_hints", f"top_{DEFAULT_RAG_TOP_K}")


@dataclass(frozen=True)
class CaseSize:
    """One case's prompt size in characters, per arm: system prompt plus the whole user message."""

    id: str
    db_path: str
    chars: dict[str, int]


def case_sizes(cases: Sequence[Case], *, evidence: bool) -> list[CaseSize]:
    """Render each case's three contexts and measure the messages they would make."""
    system = len(SQL_TRANSLATION_SYSTEM_PROMPT)
    sizes: list[CaseSize] = []
    for case in cases:
        question = question_text(case, evidence=evidence)
        db_path = resolve_db_path(case.db_path)
        selected = retrieve_schema_context(db_path, question, top_k=DEFAULT_RAG_TOP_K)
        plain_ddl, _ = get_schema_chunks_and_plain_ddl(db_path)
        contexts = {
            ARMS[0]: get_schema(db_path),
            ARMS[1]: render_schema_text(plain_ddl),
            ARMS[2]: selected.schema_text,
        }
        sizes.append(
            CaseSize(
                case.id,
                case.db_path,
                {
                    arm: system + len(build_user_prompt(context, question))
                    for arm, context in contexts.items()
                },
            )
        )
    return sizes


def render(suite: str, sizes: Sequence[CaseSize], *, context: int, chars_per_token: float) -> str:
    """The Markdown report."""
    budget = int(context * chars_per_token)
    lines = [
        f"# Prompt sizes: `{suite}` ({len(sizes)} cases)",
        "",
        f"Characters of the system prompt plus the user message as `generate_sql` builds "
        f"it, per arm. A case is over budget when its characters exceed {context} tokens x "
        f"{chars_per_token} chars/token = {budget:,} chars. The ratio is an estimate from "
        f"BIRD dev, not a bound; the run's recorded prompt tokens are the evidence after the fact.",
        "",
        "| Database | Cases | " + " | ".join(f"max {arm}" for arm in ARMS) + " |",
        "|---|---:|" + "---:|" * len(ARMS),
    ]
    by_db: dict[str, list[CaseSize]] = defaultdict(list)
    for size in sizes:
        by_db[size.db_path].append(size)
    for db_path, group in sorted(by_db.items()):
        name = Path(db_path).stem
        cells = " | ".join(f"{max(s.chars[arm] for s in group):,}" for arm in ARMS)
        lines.append(f"| `{name}` | {len(group)} | {cells} |")
    lines += ["", "## Over budget", ""]
    any_over = False
    for arm in ARMS:
        over = [s.id for s in sizes if s.chars[arm] > budget]
        if over:
            any_over = True
            shown = ", ".join(over[:20]) + (" ..." if len(over) > 20 else "")
            lines.append(f"- `{arm}`: {len(over)} of {len(sizes)} cases: {shown}")
    if not any_over:
        lines.append("No case exceeds the budget in any arm.")
    lines += [
        "",
        "Largest prompt overall: "
        + ", ".join(f"`{arm}` {max(s.chars[arm] for s in sizes):,} chars" for arm in ARMS)
        + ".",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--suite", required=True)
    parser.add_argument("--subset", default="full")
    parser.add_argument("--evidence", choices=("on", "off"), default="on")
    parser.add_argument("--context", type=int, default=32768, help="tokens the provider allows")
    parser.add_argument("--chars-per-token", type=float, default=1.6)
    parser.add_argument("--suites-dir", type=Path, default=ROOT_DIR / "evaluation" / "suites")
    args = parser.parse_args(argv)
    cases = load_suite(args.suites_dir / f"{args.suite}.jsonl")
    if args.subset != "full":
        wanted = set(read_subset_ids(args.suites_dir / f"{args.suite}.{args.subset}.txt"))
        cases = [case for case in cases if case.id in wanted]
    sizes = case_sizes(cases, evidence=args.evidence == "on")
    sys.stdout.write(
        render(args.suite, sizes, context=args.context, chars_per_token=args.chars_per_token)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
