"""scripts/report_prompt_sizes.py on the committed demo suite, whose databases are tracked."""

from __future__ import annotations

import scripts.report_prompt_sizes as script
from text_to_sql_agent.evaluation_v2 import load_suite
from text_to_sql_agent.llm import SQL_TRANSLATION_SYSTEM_PROMPT


def test_sizes_include_the_system_prompt_and_rank_the_arms() -> None:
    cases = load_suite("evaluation/suites/demo.jsonl")[:3]
    sizes = script.case_sizes(cases, evidence=False)
    assert [s.id for s in sizes] == [c.id for c in cases]
    for size in sizes:
        plain, hinted, selected = (size.chars[arm] for arm in script.ARMS)
        assert plain > len(SQL_TRANSLATION_SYSTEM_PROMPT)
        assert hinted >= plain  # hints only add
        assert selected <= hinted  # selection only removes


def test_render_names_the_cases_over_budget() -> None:
    sizes = [
        script.CaseSize("1", "data/x/a.sqlite", dict.fromkeys(script.ARMS, 100)),
        script.CaseSize(
            "2", "data/x/a.sqlite", {**dict.fromkeys(script.ARMS, 100), "plain_ddl": 901}
        ),
    ]
    report = script.render("demo", sizes, context=300, chars_per_token=3.0)
    assert "| `a` | 2 | 901 | 100 | 100 |" in report
    assert "- `plain_ddl`: 1 of 2 cases: 2" in report
    assert "No case exceeds" not in report
    assert "No case exceeds" in script.render("demo", sizes[:1], context=300, chars_per_token=3.0)
