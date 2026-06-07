from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "output",
    "temp",
    "tmp",
    ".venv",
    "venv",
    "env",
    "node_modules",
}

EXCLUDED_FILE_PATTERNS = [
    r".*\.zip$",
    r".*\.pyc$",
    r".*\.pyo$",
    r".*\.png$",
    r".*\.jpg$",
    r".*\.jpeg$",
    r".*\.webp$",
    r".*\.pt$",
    r".*\.onnx$",
    r".*\.engine$",
    r".*audit.*\.ps1$",
    r"^apply_.*\.ps1$",
    r"^stage_.*\.ps1$",
    r"^repair_.*\.ps1$",
    r"^fix_.*\.ps1$",
    r"^_tmp_.*",
]

LEGACY_HINTS = [
    "legacy",
    "old",
    "backup",
    "v12_stub",
    "stub",
    "deprecated",
    "archive",
    "unused",
]

ACTIVE_HINTS = [
    "main.py",
    "runtime",
    "solver_preflop",
    "spot_classifier",
    "range_engine",
    "clear_json_adapter",
    "v11_stage1_runtime",
    "display_analysis_cycle",
    "bridge",
    "click",
    "trigger",
]


@dataclass
class PyFileInfo:
    path: str
    relpath: str
    size_bytes: int
    category: str
    imports: list[str]
    imported_from: list[str]
    classes: list[dict[str, Any]]
    functions: list[dict[str, Any]]
    methods_count: int
    top_level_constants: list[str]
    has_main_guard: bool
    uses_argparse: bool
    uses_subprocess: bool
    uses_pytest: bool
    is_test_file: bool
    is_tool_script: bool
    is_runtime_module: bool
    is_solver_module: bool
    is_external_snapshot_module: bool
    likely_legacy: bool
    likely_active: bool
    syntax_error: str | None


def should_skip(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in EXCLUDED_DIR_NAMES for part in rel_parts):
        return True
    name = path.name
    rel = str(path.relative_to(root)).replace("\\", "/")
    for pattern in EXCLUDED_FILE_PATTERNS:
        if re.match(pattern, name, re.I) or re.match(pattern, rel, re.I):
            return True
    # Skip generated audit folders.
    if any(part.startswith("_v2_") or part.startswith("_project_source_audit") for part in rel_parts):
        return True
    return False


def classify_file(rel: str) -> str:
    r = rel.replace("\\", "/")
    if r.startswith("solver_preflop/"):
        return "solver_preflop core"
    if r.startswith("external/PokerVisionFinalVersionNoSolver_snapshot/"):
        if "/runtime/" in r:
            return "external snapshot runtime"
        if "/logic/" in r:
            return "external snapshot logic"
        if "/pipeline/" in r:
            return "external snapshot pipeline"
        return "external PokerVision snapshot"
    if r.startswith("tools/"):
        return "tools"
    if r.startswith("tests/"):
        return "tests"
    if "/fixtures/" in r or r.startswith("tests/fixtures/"):
        return "fixtures"
    return "other project python"


def extract_import_name(node: ast.AST) -> tuple[list[str], list[str]]:
    imports: list[str] = []
    imported_from: list[str] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            imports.append(alias.name)
    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        if node.level:
            module = "." * node.level + module
        imported_from.append(module)
    return imports, imported_from


def is_main_guard(node: ast.AST) -> bool:
    if not isinstance(node, ast.If):
        return False
    text = ast.dump(node.test)
    return "__name__" in text and "__main__" in text


def parse_py_file(path: Path, root: Path) -> PyFileInfo:
    rel = str(path.relative_to(root)).replace("\\", "/")
    text = path.read_text(encoding="utf-8", errors="ignore")
    syntax_error: str | None = None

    imports: list[str] = []
    imported_from: list[str] = []
    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []
    methods_count = 0
    constants: list[str] = []
    has_main = False

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        tree = None
        syntax_error = f"{exc.__class__.__name__}: {exc}"

    if tree is not None:
        for node in tree.body:
            imp, frm = extract_import_name(node)
            imports.extend(imp)
            imported_from.extend(frm)

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append(target.id)
            elif isinstance(node, ast.AnnAssign):
                target = node.target
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append(target.id)

            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "lineno": node.lineno,
                        "args_count": len(node.args.args),
                        "is_async": False,
                    }
                )
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "lineno": node.lineno,
                        "args_count": len(node.args.args),
                        "is_async": True,
                    }
                )
            elif isinstance(node, ast.ClassDef):
                method_names = [
                    item.name
                    for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                methods_count += len(method_names)
                classes.append(
                    {
                        "name": node.name,
                        "lineno": node.lineno,
                        "methods": method_names,
                        "methods_count": len(method_names),
                    }
                )

            if is_main_guard(node):
                has_main = True

        for node in ast.walk(tree):
            imp, frm = extract_import_name(node)
            if node not in tree.body:
                imports.extend(imp)
                imported_from.extend(frm)

    lower_text = text.lower()
    lower_rel = rel.lower()

    likely_legacy = any(hint in lower_rel or hint in lower_text[:5000] for hint in LEGACY_HINTS)
    likely_active = any(hint in lower_rel for hint in ACTIVE_HINTS) or has_main

    return PyFileInfo(
        path=str(path),
        relpath=rel,
        size_bytes=path.stat().st_size,
        category=classify_file(rel),
        imports=sorted(set(imports)),
        imported_from=sorted(set(imported_from)),
        classes=classes,
        functions=functions,
        methods_count=methods_count,
        top_level_constants=sorted(set(constants)),
        has_main_guard=has_main,
        uses_argparse=("argparse" in imports or "argparse" in imported_from or "argparse." in lower_text),
        uses_subprocess=("subprocess" in imports or "subprocess" in imported_from or "subprocess." in lower_text),
        uses_pytest=("pytest" in imports or "pytest" in imported_from or "pytest" in lower_text),
        is_test_file=(rel.startswith("tests/") or Path(rel).name.startswith("test_")),
        is_tool_script=rel.startswith("tools/"),
        is_runtime_module=("/runtime/" in rel or rel.startswith("runtime/")),
        is_solver_module=rel.startswith("solver_preflop/"),
        is_external_snapshot_module=rel.startswith("external/PokerVisionFinalVersionNoSolver_snapshot/"),
        likely_legacy=likely_legacy,
        likely_active=likely_active,
        syntax_error=syntax_error,
    )


def git_tracked_files(root: Path) -> set[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=str(root),
            check=True,
            text=True,
            capture_output=True,
        )
        return {line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()}
    except Exception:
        return set()


def collect_pytest_tests(root: Path) -> dict[str, Any]:
    tests: list[str] = []
    try:
        completed = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q"],
            cwd=str(root),
            text=True,
            capture_output=True,
            timeout=90,
        )
        for line in completed.stdout.splitlines():
            line = line.strip()
            if line and ("::" in line or line.endswith(".py")):
                tests.append(line)
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "collected_count_estimate": len(tests),
            "items_sample": tests[:200],
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "collected_count_estimate": 0,
            "items_sample": [],
        }


def build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = report["summary"]
    lines.append("# V2.54 Project Static Logic Map")
    lines.append("")
    lines.append("## Summary")
    for key, value in summary.items():
        lines.append(f"- **{key}**: `{value}`")

    lines.append("")
    lines.append("## Categories")
    for category, rows in report["by_category"].items():
        lines.append(f"### {category}")
        lines.append(f"- files: `{len(rows)}`")
        for row in rows[:80]:
            lines.append(
                f"- `{row['relpath']}` "
                f"classes={len(row['classes'])} functions={len(row['functions'])} "
                f"methods={row['methods_count']} main={row['has_main_guard']} "
                f"argparse={row['uses_argparse']} pytest={row['uses_pytest']} "
                f"legacy={row['likely_legacy']} active={row['likely_active']}"
            )
        if len(rows) > 80:
            lines.append(f"- ... `{len(rows) - 80}` more")

    lines.append("")
    lines.append("## Entrypoints")
    for row in report["entrypoints"]:
        lines.append(f"- `{row['relpath']}` category=`{row['category']}` argparse=`{row['uses_argparse']}`")

    lines.append("")
    lines.append("## Tool scripts")
    for row in report["tools"][:160]:
        lines.append(f"- `{row['relpath']}` main={row['has_main_guard']} argparse={row['uses_argparse']} subprocess={row['uses_subprocess']}")

    lines.append("")
    lines.append("## Tests")
    for row in report["tests"][:180]:
        fn_names = [fn["name"] for fn in row["functions"] if fn["name"].startswith("test")]
        lines.append(f"- `{row['relpath']}` test_functions={fn_names[:12]} uses_pytest={row['uses_pytest']}")

    lines.append("")
    lines.append("## Likely active files")
    for row in report["likely_active_files"][:160]:
        lines.append(f"- `{row['relpath']}` category=`{row['category']}`")

    lines.append("")
    lines.append("## Likely legacy / dead candidates")
    lines.append("These are candidates only. Do not delete without dynamic execution proof.")
    for row in report["likely_legacy_files"][:200]:
        lines.append(f"- `{row['relpath']}` category=`{row['category']}`")

    lines.append("")
    lines.append("## Syntax errors")
    if not report["syntax_errors"]:
        lines.append("- none")
    else:
        for row in report["syntax_errors"]:
            lines.append(f"- `{row['relpath']}`: `{row['syntax_error']}`")

    lines.append("")
    lines.append("## Pytest collect")
    pc = report.get("pytest_collect", {})
    lines.append(f"- ok: `{pc.get('ok')}`")
    lines.append(f"- collected_count_estimate: `{pc.get('collected_count_estimate')}`")
    if pc.get("error"):
        lines.append(f"- error: `{pc.get('error')}`")
    if pc.get("stderr_tail"):
        lines.append("")
        lines.append("```text")
        lines.append(str(pc.get("stderr_tail"))[-3000:])
        lines.append("```")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build static project logic map for PokerVision_Solver_Preflop.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output-json", default="outputs/v2_54_project_static_logic_map.json")
    parser.add_argument("--output-md", default="outputs/v2_54_project_static_logic_map.md")
    parser.add_argument("--skip-pytest-collect", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    py_files = [
        path
        for path in root.rglob("*.py")
        if path.is_file() and not should_skip(path, root)
    ]
    py_files.sort(key=lambda p: str(p.relative_to(root)).lower())

    infos = [parse_py_file(path, root) for path in py_files]
    info_dicts = [asdict(info) for info in infos]

    tracked = git_tracked_files(root)

    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for info in info_dicts:
        by_category[info["category"]].append(info)

    imports_counter = Counter()
    for info in infos:
        imports_counter.update(info.imports)
        imports_counter.update(info.imported_from)

    entrypoints = [asdict(info) for info in infos if info.has_main_guard or info.uses_argparse]
    tools = [asdict(info) for info in infos if info.is_tool_script]
    tests = [asdict(info) for info in infos if info.is_test_file or info.uses_pytest]
    likely_legacy = [asdict(info) for info in infos if info.likely_legacy]
    likely_active = [asdict(info) for info in infos if info.likely_active]
    syntax_errors = [asdict(info) for info in infos if info.syntax_error]

    summary = {
        "project_root": str(root),
        "python_files_total": len(infos),
        "git_tracked_files_total": len(tracked),
        "entrypoints_total": len(entrypoints),
        "tool_scripts_total": len(tools),
        "tests_total": len(tests),
        "runtime_modules_total": sum(1 for info in infos if info.is_runtime_module),
        "solver_modules_total": sum(1 for info in infos if info.is_solver_module),
        "external_snapshot_modules_total": sum(1 for info in infos if info.is_external_snapshot_module),
        "likely_active_total": len(likely_active),
        "likely_legacy_total": len(likely_legacy),
        "syntax_errors_total": len(syntax_errors),
        "classes_total": sum(len(info.classes) for info in infos),
        "functions_total": sum(len(info.functions) for info in infos),
        "methods_total": sum(info.methods_count for info in infos),
    }

    report: dict[str, Any] = {
        "schema": "v2_54_project_static_logic_map_v1",
        "summary": summary,
        "files": info_dicts,
        "by_category": {k: v for k, v in sorted(by_category.items())},
        "entrypoints": entrypoints,
        "tools": tools,
        "tests": tests,
        "likely_legacy_files": likely_legacy,
        "likely_active_files": likely_active,
        "syntax_errors": syntax_errors,
        "top_imports": imports_counter.most_common(100),
        "pytest_collect": {} if args.skip_pytest_collect else collect_pytest_tests(root),
    }

    out_json = root / args.output_json
    out_md = root / args.output_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(build_markdown(report), encoding="utf-8")

    print("V2.54 PROJECT STATIC LOGIC MAP")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("-" * 100)
    print(f"output_json={out_json}")
    print(f"output_md={out_md}")
    # Syntax errors are findings in the static map, not a fatal failure.
    # The project contains generated/legacy/probe Python fragments; the auditor
    # must report them so cleanup can be planned later.
    ok = summary["python_files_total"] > 0
    print(f"V2.54_PROJECT_STATIC_LOGIC_MAP_OK = {ok}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
