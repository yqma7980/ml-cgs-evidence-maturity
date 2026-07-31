#!/usr/bin/env python3
"""Complete cited IJGGC bibliography metadata without trusting a DOI blindly."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / "manuscript" / "international-journal-of-greenhouse-gas-control-v2-wp8-r2" / "main.tex"
BIB = TEX.parent / "references_submission_cleaned_v3.bib"
OVERRIDES = ROOT / "config" / "ijggc_v2_reference_metadata_overrides.json"
CACHE = ROOT / "validation" / "IJGGC_V2_CROSSREF_METADATA_CACHE_R2.json"
AUDIT = ROOT / "validation" / "IJGGC_V2_REFERENCE_METADATA_COMPLETION_R2.csv"
REPORT = ROOT / "validation" / "IJGGC_V2_REFERENCE_IDENTITY_REPAIR_REPORT.md"


def normalized(value: str) -> str:
    value = re.sub(r"CO\s*<mml:math.*?</mml:math>", "CO2", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<mml:math.*?</mml:math>", "CO2", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\\[A-Za-z]+", " ", value)
    value = value.replace("{", "").replace("}", "")
    value = value.replace("$_2$", "2").replace("₂", "2")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def title_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalized(left), normalized(right)).ratio()


def cited_keys() -> set[str]:
    text = TEX.read_text(encoding="utf-8")
    keys: set[str] = set()
    for match in re.finditer(r"\\cite\w*\{([^}]+)\}", text):
        keys.update(item.strip() for item in match.group(1).split(",") if item.strip())
    return keys


def entry_blocks(text: str) -> list[tuple[str, int, int, str]]:
    blocks: list[tuple[str, int, int, str]] = []
    for match in re.finditer(r"@\w+\{([^,]+),", text):
        depth = 0
        started = False
        end = None
        for index in range(match.start(), len(text)):
            char = text[index]
            if char == "{":
                depth += 1
                started = True
            elif char == "}":
                depth -= 1
                if started and depth == 0:
                    end = index + 1
                    break
        if end is None:
            raise ValueError(f"Unclosed BibTeX entry: {match.group(1)}")
        blocks.append((match.group(1).strip(), match.start(), end, text[match.start():end]))
    return blocks


def field(block: str, name: str) -> str:
    match = re.search(rf"(?ims)^\s*{re.escape(name)}\s*=\s*\{{(.*?)\}}\s*,?\s*$", block)
    return match.group(1).strip() if match else ""


def set_field(block: str, name: str, value: str) -> str:
    pattern = rf"(?ims)^(\s*{re.escape(name)}\s*=\s*)\{{.*?\}}(\s*,?\s*)$"
    if re.search(pattern, block):
        return re.sub(pattern, lambda m: f"{m.group(1)}{{{value}}}{m.group(2)}", block, count=1)
    closing = block.rfind("}")
    prefix = block[:closing].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    return prefix + f"\n  {name} = {{{value}}}\n" + block[closing:]


def crossref_message(doi: str, cache: dict[str, dict[str, object]]) -> tuple[dict[str, object] | None, str]:
    key = doi.lower()
    if key in cache:
        return cache[key], "cache"
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ML-CGS-evidence-review/2.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            message = json.load(response)["message"]
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
        return None, f"request_error: {exc}"
    selected = {
        "DOI": message.get("DOI", ""),
        "title": message.get("title", []),
        "container-title": message.get("container-title", []),
        "volume": message.get("volume", ""),
        "issue": message.get("issue", ""),
        "page": message.get("page", ""),
        "article-number": message.get("article-number", ""),
        "published": message.get("published", {}),
    }
    cache[key] = selected
    time.sleep(0.08)
    return selected, "crossref"


def first(value: object) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")


def main() -> None:
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    cited = cited_keys()
    original = BIB.read_text(encoding="utf-8")
    blocks = entry_blocks(original)
    replacements: dict[str, str] = {}
    rows: list[dict[str, object]] = []

    for key, _start, _end, block in blocks:
        if key not in cited:
            continue
        doi = field(block, "doi").removeprefix("https://doi.org/").strip()
        current_title = field(block, "title")
        updated = block
        changed: list[str] = []
        forced = key in overrides

        if forced:
            item = overrides[key]
            mapped = {
                "author": str(item.get("authors", "")).replace("; ", " and "),
                "title": str(item.get("title", "")),
                "journal": str(item.get("venue", "")),
                "year": str(item.get("year", "")),
                "volume": str(item.get("volume", "")),
                "number": str(item.get("number", "")),
                "pages": str(item.get("pages", "")),
                "doi": str(item.get("doi_or_url", "")).removeprefix("https://doi.org/"),
            }
            for name, value in mapped.items():
                if value and field(updated, name) != value:
                    updated = set_field(updated, name, value)
                    changed.append(name)
            doi = mapped["doi"]
            current_title = mapped["title"]

        if not doi:
            rows.append({
                "citation_key": key,
                "doi": "",
                "identity_status": "no_doi",
                "title_similarity": "",
                "updated_fields": ";".join(changed),
                "crossref_title": "",
                "notes": "No DOI available; retained for human review.",
            })
            replacements[key] = updated
            continue

        message, source = crossref_message(doi, cache)
        if not message:
            rows.append({
                "citation_key": key,
                "doi": doi,
                "identity_status": "crossref_unavailable",
                "title_similarity": "",
                "updated_fields": ";".join(changed),
                "crossref_title": "",
                "notes": source,
            })
            replacements[key] = updated
            continue

        crossref_title = first(message.get("title"))
        similarity = title_similarity(current_title, crossref_title)
        identity_ok = forced or similarity >= 0.72
        if identity_ok:
            candidates = {
                "volume": first(message.get("volume")),
                "number": first(message.get("issue")),
                "pages": first(message.get("page")) or first(message.get("article-number")),
            }
            for name, value in candidates.items():
                if value and not field(updated, name):
                    updated = set_field(updated, name, value.replace("-", "--") if name == "pages" else value)
                    changed.append(name)

        rows.append({
            "citation_key": key,
            "doi": doi,
            "identity_status": "verified_override" if forced else ("title_match" if identity_ok else "title_mismatch_review"),
            "title_similarity": f"{similarity:.3f}",
            "updated_fields": ";".join(dict.fromkeys(changed)),
            "crossref_title": crossref_title,
            "notes": source if identity_ok else "No metadata added because the DOI title did not match the cited title.",
        })
        replacements[key] = updated

    rebuilt: list[str] = []
    cursor = 0
    for key, start, end, block in blocks:
        rebuilt.append(original[cursor:start])
        rebuilt.append(replacements.get(key, block))
        cursor = end
    rebuilt.append(original[cursor:])
    BIB.write_text("".join(rebuilt), encoding="utf-8")
    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fields = [
        "citation_key", "doi", "identity_status", "title_similarity",
        "updated_fields", "crossref_title", "notes",
    ]
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: str(row["citation_key"])))

    mismatch = [row for row in rows if row["identity_status"] in {"title_mismatch_review", "crossref_unavailable", "no_doi"}]
    changed_entries = [row for row in rows if row["updated_fields"]]
    REPORT.write_text(
        "# IJGGC V2 reference identity and metadata repair\n\n"
        f"- In-text citation keys audited: {len(rows)}\n"
        f"- Entries updated: {len(changed_entries)}\n"
        f"- Verified identity overrides applied: {sum(row['identity_status'] == 'verified_override' for row in rows)}\n"
        f"- Entries retained for human review: {len(mismatch)}\n"
        "- Rule: missing volume, issue, and page/article metadata were added only when the DOI title matched the cited title.\n"
        "- The four documented identity errors were repaired from the author-verified override file.\n\n"
        "## Remaining review items\n\n"
        + ("\n".join(f"- {row['citation_key']}: {row['identity_status']}" for row in mismatch) if mismatch else "None.")
        + "\n",
        encoding="utf-8",
    )
    print(f"Audited {len(rows)} cited entries; updated {len(changed_entries)}; review items {len(mismatch)}")


if __name__ == "__main__":
    main()
