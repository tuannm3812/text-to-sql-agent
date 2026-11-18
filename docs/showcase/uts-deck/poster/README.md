# UTS poster blocks

Native poster blocks and styles for the deck-kit poster engine, following [the poster template](../POSTER-TEMPLATE.md).
Reference build: the Synogize harness poster (`project-15-strategy/deliverables/portfolio-showcase/uts-deck/poster/`).

In a poster spec:

```json
{"plugin": "<kit>/templates/poster/uts_poster_blocks.py", "css": "<kit>/templates/poster/uts_poster.css"}
```

Use `uts_poster_landscape.css` for landscape. Each block's fields are listed at the top of `uts_poster_blocks.py`.
Verified 17 November 2026 by rendering the Synogize portrait and landscape posters from these copies (no problems,
text identical to the project build).
