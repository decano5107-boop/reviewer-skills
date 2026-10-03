#!/usr/bin/env python3
"""Structural lint for the skills in this repository.

Checks, for every skills/<name>/SKILL.md:
  - the file opens with a YAML frontmatter block delimited by '---' lines
  - frontmatter has `name` and `description`
  - `name` equals the directory name and is lower-case kebab-case, at most 64 characters
  - `description` is between 50 and 1024 characters once folded
  - every relative file or directory the skill references (markdown links and
    backticked paths) exists, resolved from the skill directory or the repo root
  - every `skills/<x>` reference anywhere in the skill points at a real skill

Repository-level checks:
  - .claude-plugin/plugin.json and marketplace.json parse, and their names agree
  - README.md has a section for every skill, and no section for a skill that is gone

This is a structural check only. It does not test whether a skill gives good advice.

Usage:
  python3 scripts/lint_skills.py              lint the repository
  python3 scripts/lint_skills.py --self-test  prove the linter catches broken fixtures
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DESC_MIN, DESC_MAX = 50, 1024
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
TICK_RE = re.compile(r"`([^`\s]+)`")
SKILL_REF_RE = re.compile(r"\bskills/([a-z0-9-]+)")
README_SECTION_RE = re.compile(r"^###\s+`([a-z0-9-]+)`", re.M)


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Minimal parser for top-level `key: value` and folded/literal block scalars."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing opening '---'"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, "missing closing '---'"
    fields: dict[str, str] = {}
    key = None
    buf: list[str] = []
    for raw in lines[1:end]:
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if m and not raw.startswith((" ", "\t")):
            if key is not None:
                fields[key] = " ".join(x.strip() for x in buf if x.strip())
            key, value = m.group(1), m.group(2).strip()
            buf = [] if value in (">", ">-", "|", "|-", "") else [value.strip("\"'")]
        elif key is not None:
            buf.append(raw)
    if key is not None:
        fields[key] = " ".join(x.strip() for x in buf if x.strip())
    return fields, ""


def looks_like_path(token: str) -> bool:
    if token.startswith(("http://", "https://", "mailto:", "#", "~", "/", "$")):
        return False
    if any(c in token for c in "<>*{}|="):
        return False
    return "/" in token and (token.endswith("/") or re.search(r"\.(md|py|json|ya?ml|sh|txt)$", token) is not None)


def lint(root: Path) -> list[str]:
    errors: list[str] = []
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return [f"{skills_dir}: no skills/ directory"]
    skill_names = sorted(p.name for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skill_names:
        errors.append("skills/: no skills found")

    for name in skill_names:
        sdir = skills_dir / name
        skill_md = sdir / "SKILL.md"
        rel = skill_md.relative_to(root)
        if not skill_md.is_file():
            errors.append(f"{rel}: missing")
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm, why = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: bad frontmatter ({why})")
            continue
        fname = fm.get("name", "")
        desc = fm.get("description", "")
        if not fname:
            errors.append(f"{rel}: frontmatter has no name")
        elif fname != name:
            errors.append(f"{rel}: name '{fname}' does not match directory '{name}'")
        elif not NAME_RE.match(fname) or len(fname) > 64:
            errors.append(f"{rel}: name '{fname}' is not lower-case kebab-case of at most 64 chars")
        if not desc:
            errors.append(f"{rel}: frontmatter has no description")
        elif not DESC_MIN <= len(desc) <= DESC_MAX:
            errors.append(f"{rel}: description is {len(desc)} chars (allowed {DESC_MIN}-{DESC_MAX})")

        refs = set(LINK_RE.findall(text)) | {t for t in TICK_RE.findall(text) if looks_like_path(t)}
        for ref in sorted(refs):
            if ref.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = ref.split("#", 1)[0]
            if not ((sdir / target).exists() or (root / target).exists()):
                errors.append(f"{rel}: references '{ref}', which does not exist")
        for other in sorted(set(SKILL_REF_RE.findall(text))):
            if other not in skill_names:
                errors.append(f"{rel}: references skill 'skills/{other}', which does not exist")

    plugin = root / ".claude-plugin" / "plugin.json"
    market = root / ".claude-plugin" / "marketplace.json"
    try:
        pj = json.loads(plugin.read_text(encoding="utf-8"))
        mj = json.loads(market.read_text(encoding="utf-8"))
        names = [p.get("name") for p in mj.get("plugins", [])]
        if pj.get("name") not in names:
            errors.append(f"marketplace.json does not list plugin '{pj.get('name')}' (lists {names})")
    except (OSError, ValueError) as e:
        errors.append(f".claude-plugin: {e}")

    readme = root / "README.md"
    if readme.is_file():
        listed = set(README_SECTION_RE.findall(readme.read_text(encoding="utf-8")))
        for name in skill_names:
            if name not in listed:
                errors.append(f"README.md: no section for skill '{name}'")
        for name in sorted(listed - set(skill_names)):
            errors.append(f"README.md: section for '{name}', which is not in skills/")
    else:
        errors.append("README.md: missing")
    return errors


GOOD_SKILL = """---
name: {name}
description: >-
  A fixture skill used only by the self-test. It exists to give the linter a valid
  example to pass before the broken variants are checked.
---

# Fixture

See `reference/notes.md`.
"""


def build_fixture(base: Path, skill_text: str, name: str = "demo-skill", with_ref: bool = True) -> Path:
    root = base / name
    sdir = root / "skills" / name
    sdir.mkdir(parents=True)
    (sdir / "SKILL.md").write_text(skill_text.format(name=name), encoding="utf-8")
    if with_ref:
        (sdir / "reference").mkdir()
        (sdir / "reference" / "notes.md").write_text("x\n", encoding="utf-8")
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text('{"name": "p"}', encoding="utf-8")
    (root / ".claude-plugin" / "marketplace.json").write_text('{"plugins": [{"name": "p"}]}', encoding="utf-8")
    (root / "README.md").write_text(f"### `{name}`\n", encoding="utf-8")
    return root


def self_test() -> bool:
    cases = [
        ("valid skill passes", GOOD_SKILL, {}, None),
        ("missing frontmatter", "# no frontmatter\n", {}, "bad frontmatter"),
        ("name mismatch", GOOD_SKILL.replace("name: {name}", "name: other"), {}, "does not match directory"),
        ("short description", "---\nname: {name}\ndescription: too short\n---\n", {}, "description is"),
        ("missing referenced file", GOOD_SKILL, {"with_ref": False}, "does not exist"),
        ("dangling skill reference", GOOD_SKILL + "\nPairs with skills/ghost-skill.\n", {}, "skills/ghost-skill"),
    ]
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for i, (label, text, kw, expect) in enumerate(cases):
            root = build_fixture(Path(tmp) / str(i), text, **kw)
            errs = lint(root)
            passed = (not errs) if expect is None else any(expect in e for e in errs)
            print(f"  {'ok  ' if passed else 'FAIL'} {label}" + ("" if passed else f" -> {errs}"))
            ok &= passed
    print("[lint_skills] self-test " + ("passed" if ok else "FAILED"))
    return ok


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return 0 if self_test() else 1
    root = Path(__file__).resolve().parent.parent
    errors = lint(root)
    for e in errors:
        print(f"  error: {e}")
    n = len([p for p in (root / "skills").iterdir() if p.is_dir() and not p.name.startswith(".")])
    print(f"[lint_skills] {n} skill(s), {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
