"""Rules that check each CSV row, and the references between rows, against the tag model."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from .tags import ENTITY_TAGS, FUNCTION_TAGS, KINDS, KNOWN_TAGS, TAG_NAME


@dataclass(frozen=True)
class Issue:
    """One finding. `line` is the CSV line number (the header is line 1)."""

    line: int
    rule: str
    id: str
    message: str

    def __str__(self) -> str:
        return f"line {self.line} {self.rule} [{self.id or '-'}] {self.message}"


def validate_rows(rows: Iterable[dict[str, str]]) -> list[Issue]:
    """Validate parsed rows with columns id, dis, markers, equipRef, siteRef, kind, unit."""
    rows = list(rows)
    issues: list[Issue] = []
    ids = Counter((r.get("id") or "").strip() for r in rows)
    entity_of: dict[str, str] = {}
    for row in rows:
        rid = (row.get("id") or "").strip()
        found = [t for t in dict.fromkeys((row.get("markers") or "").split()) if t in ENTITY_TAGS]
        if rid and len(found) == 1:
            entity_of[rid] = found[0]

    for number, row in enumerate(rows, start=2):
        rid = (row.get("id") or "").strip()

        def add(rule: str, message: str, number: int = number, rid: str = rid) -> None:
            issues.append(Issue(number, rule, rid, message))

        if not rid:
            add("H001", "row has no id")
        elif ids[rid] > 1:
            add("H002", f"id used {ids[rid]} times")

        tags = (row.get("markers") or "").split()
        for tag, count in Counter(tags).items():
            if count > 1:
                add("H003", f"marker '{tag}' repeated")
        for tag in dict.fromkeys(tags):
            if not TAG_NAME.match(tag):
                add("H004", f"tag name '{tag}' is not valid camelCase")
            elif tag not in KNOWN_TAGS:
                add("H005", f"unknown tag '{tag}'")

        entities = [t for t in dict.fromkeys(tags) if t in ENTITY_TAGS]
        if len(entities) != 1:
            add("H006", f"needs exactly one entity tag, found {len(entities)}")
            continue
        entity = entities[0]

        if entity == "point":
            funcs = [t for t in dict.fromkeys(tags) if t in FUNCTION_TAGS]
            if len(funcs) != 1:
                add("H007", f"point needs one of sensor, cmd, sp; found {len(funcs)}")
            _check_ref(add, "equipRef", (row.get("equipRef") or "").strip(), "equip", entity_of)
            kind = (row.get("kind") or "").strip()
            if kind not in KINDS:
                add("H009", f"kind '{kind}' must be one of Bool, Number, Str")
            elif kind == "Number" and not (row.get("unit") or "").strip():
                add("H010", "Number point has no unit")
        elif entity == "equip":
            _check_ref(add, "siteRef", (row.get("siteRef") or "").strip(), "site", entity_of)
    return issues


def _check_ref(
    add: Callable[[str, str], None],
    column: str,
    value: str,
    wanted: str,
    entity_of: dict[str, str],
) -> None:
    """Report a missing reference or one that points to the wrong kind of entity."""
    if not value:
        add("H008", f"{column} is missing")
    elif entity_of.get(value) != wanted:
        add("H008", f"{column} '{value}' matches no {wanted}")


def validate_file(path: str | Path) -> list[Issue]:
    """Read a CSV file and validate it."""
    with open(path, newline="", encoding="utf-8") as handle:
        return validate_rows(csv.DictReader(handle))
