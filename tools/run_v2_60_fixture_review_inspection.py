from __future__ import annotations

import argparse, hashlib, json, subprocess
from collections import Counter
from pathlib import Path
from typing import Any

CURRENT_HINTS = [f"v2_{i}" for i in range(42, 61)]
MAX_READ = 8_000_000
MAX_PREVIEW = 2200


def run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=60)
        return {"ok": p.returncode == 0, "stdout": p.stdout, "stderr": p.stderr, "returncode": p.returncode}
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e), "returncode": None}


def git_tracked(root: Path) -> set[str]:
    r = run(["git", "ls-files"], root)
    return {x.strip().replace("\\", "/") for x in r["stdout"].splitlines() if x.strip()} if r["ok"] else set()


def git_status(root: Path) -> dict[str, str]:
    r = run(["git", "status", "--short"], root)
    out = {}
    if r["ok"]:
        for line in r["stdout"].splitlines():
            if len(line) >= 4 and line.strip():
                out[line[3:].strip().replace("\\", "/")] = line[:2]
    return out


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 256), b""):
            h.update(b)
    return h.hexdigest()


def shape(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        keys = list(data.keys())
        s: dict[str, Any] = {"top_type": "dict", "keys_count": len(keys), "keys": keys[:60]}
        if isinstance(data.get("cases"), list):
            cases = data["cases"]
            s["cases_len"] = len(cases)
            s["first_case_keys"] = list(cases[0].keys())[:60] if cases and isinstance(cases[0], dict) else None
        return s
    if isinstance(data, list):
        return {
            "top_type": "list",
            "list_len": len(data),
            "first_item_type": type(data[0]).__name__ if data else None,
            "first_item_keys": list(data[0].keys())[:60] if data and isinstance(data[0], dict) else None,
        }
    return {"top_type": type(data).__name__}


def preview(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)[:MAX_PREVIEW]
    except Exception:
        return str(data)[:MAX_PREVIEW]


def keep_rows(v259: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in v259.get("json_files", []) if r.get("group") in {"FIXTURE_TRUTH_SOURCE_KEEP", "CURRENT_REFERENCED_KEEP"}]


def similar_current(rel: str, keep: list[dict[str, Any]]) -> list[dict[str, Any]]:
    name = Path(rel).name.lower()
    tokens = {t for t in str(Path(rel).parent).lower().replace("\\", "/").replace(".", "_").split("_") if t}
    out = []
    for row in keep:
        other = row.get("relpath", "")
        if other == rel:
            continue
        score, reasons = 0, []
        if Path(other).name.lower() == name:
            score += 5
            reasons.append("same_filename")
        other_tokens = set(str(Path(other).parent).lower().replace("\\", "/").replace(".", "_").split("_"))
        overlap = sorted((tokens & other_tokens) - {"tests", "fixtures", "case", "cases", "json"})
        if overlap:
            score += len(overlap)
            reasons.append("folder_overlap=" + ",".join(overlap[:5]))
        if any(h in other.lower() for h in CURRENT_HINTS):
            score += 2
            reasons.append("current_version_hint")
        if score:
            out.append({"relpath": other, "score": score, "reasons": reasons, "group": row.get("group")})
    return sorted(out, key=lambda x: (-x["score"], x["relpath"]))[:10]


def recommend(rel: str, exists: bool, refs: int, shp: dict[str, Any], dup: str | None, sims: list[dict[str, Any]]) -> tuple[str, list[str]]:
    if not exists:
        return "DELETE_CANDIDATE", ["file already missing"]
    if refs > 0:
        return "KEEP", ["referenced by project"]
    if dup:
        return "DELETE_CANDIDATE", [f"byte-identical duplicate of {dup}"]
    if any(h in rel.lower() for h in CURRENT_HINTS):
        return "KEEP", ["current version hint in path"]

    keys = set(shp.get("keys") or [])
    first_case = set(shp.get("first_case_keys") or [])
    if shp.get("cases_len") is not None:
        reasons = [f"cases_len={shp.get('cases_len')}"]
        if {"expected", "category", "players", "hero_cards", "clear_json", "solver", "runtime"} & (keys | first_case):
            if sims:
                return "MIGRATE_TO_CURRENT_FIXTURE", reasons + ["test-like cases with similar current fixture"]
            return "ARCHIVE_CANDIDATE", reasons + ["test-like cases but unreferenced"]
        return "ARCHIVE_CANDIDATE", reasons + ["unreferenced cases fixture"]
    if sims:
        return "MIGRATE_TO_CURRENT_FIXTURE", ["valid JSON with similar current fixture"]
    return "ARCHIVE_CANDIDATE", ["valid unreferenced fixture JSON"]


def build_md(report: dict[str, Any]) -> str:
    lines = ["# V2.60 Fixture Review Inspection", "", "## Summary"]
    for k, v in report["summary"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines += [
        "",
        "## Policy",
        "- This report does **not** delete or move files.",
        "- `MIGRATE_TO_CURRENT_FIXTURE` means inspect and possibly merge useful cases into current V2 fixtures.",
        "- `ARCHIVE_CANDIDATE` means remove from active path later only after review.",
    ]
    for group in ["KEEP", "MIGRATE_TO_CURRENT_FIXTURE", "ARCHIVE_CANDIDATE", "DELETE_CANDIDATE"]:
        rows = [r for r in report["fixtures"] if r["recommendation"] == group]
        lines += ["", f"## {group}"]
        if not rows:
            lines.append("- none")
        for r in rows:
            lines.append(f"- `{r['relpath']}` tracked=`{r['git_tracked']}` refs=`{r['references_count']}` size=`{r['size_bytes']}` reasons=`{'; '.join(r['recommendation_reasons'])}`")
            if r["similar_current_fixtures"]:
                lines.append(f"  - similar_current: `{r['similar_current_fixtures'][:5]}`")
            if r.get("preview"):
                lines.append("  ```json")
                lines.append("  " + r["preview"][:800].replace("\n", "\n  "))
                lines.append("  ```")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect V2.59 FIXTURE_REVIEW JSON files.")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--trust-json", default="outputs/v2_59_fixture_json_trust_review.json")
    ap.add_argument("--output-json", default="outputs/v2_60_fixture_review_inspection.json")
    ap.add_argument("--output-md", default="outputs/v2_60_fixture_review_inspection.md")
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    trust_path = (root / args.trust_json).resolve()
    v259 = load_json(trust_path)
    tracked = git_tracked(root)
    status = git_status(root)
    keep = keep_rows(v259)

    keep_sha = {}
    for r in keep:
        rel = r.get("relpath")
        if rel:
            digest = sha256(root / rel)
            if digest:
                keep_sha[digest] = rel

    targets = [r for r in v259.get("json_files", []) if r.get("group") == "FIXTURE_REVIEW"]
    inspected = []
    print("V2.60 FIXTURE REVIEW INSPECTION")
    print(f"fixture_review_total: {len(targets)}")
    for i, row in enumerate(targets, 1):
        rel = row["relpath"]
        path = root / rel
        exists = path.exists()
        print(f"[v2.60] inspect {i}/{len(targets)}: {rel}", flush=True)
        data, parse_error = None, None
        try:
            if exists and path.stat().st_size <= MAX_READ:
                data = load_json(path)
            elif exists:
                parse_error = "skipped_large"
        except Exception as e:
            parse_error = f"{type(e).__name__}: {e}"
        shp = shape(data) if data is not None else {"top_type": None, "parse_error": parse_error}
        digest = sha256(path)
        dup = keep_sha.get(digest) if digest else None
        sims = similar_current(rel, keep)
        refs = int(row.get("references_count") or 0)
        rec, reasons = recommend(rel, exists, refs, shp, dup, sims)
        inspected.append({
            "relpath": rel,
            "exists": exists,
            "git_tracked": rel in tracked,
            "git_status": status.get(rel, ""),
            "size_bytes": path.stat().st_size if exists else None,
            "sha256": digest,
            "references_count": refs,
            "references_sample": row.get("references_sample") or [],
            "shape": shp,
            "duplicate_keep_match": dup,
            "similar_current_fixtures": sims,
            "recommendation": rec,
            "recommendation_reasons": reasons,
            "original_v259_row": row,
            "preview": preview(data) if data is not None else "",
        })

    counts = Counter(x["recommendation"] for x in inspected)
    summary = {
        "project_root": str(root),
        "trust_json": str(trust_path),
        "fixture_review_total": len(inspected),
        "keep_total": counts.get("KEEP", 0),
        "migrate_to_current_fixture_total": counts.get("MIGRATE_TO_CURRENT_FIXTURE", 0),
        "archive_candidate_total": counts.get("ARCHIVE_CANDIDATE", 0),
        "delete_candidate_total": counts.get("DELETE_CANDIDATE", 0),
        "recommendation_counts": dict(counts),
    }
    report = {"schema": "v2_60_fixture_review_inspection_v1", "summary": summary, "fixtures": inspected}
    outj = root / args.output_json
    outm = root / args.output_md
    outj.parent.mkdir(parents=True, exist_ok=True)
    outj.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    outm.write_text(build_md(report), encoding="utf-8")

    print("-" * 100)
    for k, v in summary.items():
        print(f"{k}: {v}")
    print("-" * 100)
    for item in inspected:
        print(f"{item['recommendation']:28} refs={item['references_count']} size={item['size_bytes']} path={item['relpath']}")
    print("-" * 100)
    print(f"output_json={outj}")
    print(f"output_md={outm}")
    ok = len(inspected) == len(targets)
    print(f"V2.60_FIXTURE_REVIEW_INSPECTION_OK = {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
