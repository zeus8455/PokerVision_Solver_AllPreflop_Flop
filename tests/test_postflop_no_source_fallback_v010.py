from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Iterable

from solver_postflop import ClearJsonInput, build_solver_input, load_clear_json_input


POSTFLOP_SOURCE_FILES = (
    Path("solver_postflop/__init__.py"),
    Path("solver_postflop/engine_contracts.py"),
    Path("solver_postflop/clear_json_input.py"),
    Path("solver_postflop/solver_input.py"),
)


FORBIDDEN_ARCHITECTURE_MARKERS = (
    "Dark_JSON",
    "Pending_JSON",
    "Service JSON",
    "Runtime JSON",
    "dark_json",
    "pending_json",
    "service_json",
    "runtime_json",
    "source_discovery",
    "display_analysis_cycle",
    "Action_Button",
    "PokerVisionFinalVersionNoSolver_snapshot",
    "solver_preflop",
    "external.",
    "glob(",
    "rglob(",
    "os.walk",
    "iterdir(",
    "duplicate",
    "collision",
    "hero-board",
    "filter players",
    "filter_players",
    "create HERO",
    "create_hero",
    "runtime",
    "click",
)


FORBIDDEN_IMPORT_ROOTS = {
    "solver_preflop",
    "external",
    "display_analysis_cycle",
    "Action_Button",
    "runtime",
    "source_discovery",
}


def _read_source_tree() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in POSTFLOP_SOURCE_FILES)


def _iter_import_roots(path: Path) -> Iterable[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".", 1)[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module.split(".", 1)[0]


def test_postflop_source_tree_has_no_fallback_or_validation_markers() -> None:
    source_text = _read_source_tree()

    for marker in FORBIDDEN_ARCHITECTURE_MARKERS:
        assert marker not in source_text


def test_postflop_modules_do_not_import_preflop_or_live_chain() -> None:
    imported_roots = {
        import_root
        for source_file in POSTFLOP_SOURCE_FILES
        for import_root in _iter_import_roots(source_file)
    }

    assert imported_roots.isdisjoint(FORBIDDEN_IMPORT_ROOTS)


def test_importing_solver_postflop_does_not_load_preflop_or_live_modules() -> None:
    __import__("solver_postflop")

    forbidden_loaded_modules = (
        "solver_preflop",
        "display_analysis_cycle",
        "source_discovery",
        "Action_Button",
    )

    for module_name in forbidden_loaded_modules:
        assert module_name not in sys.modules


def test_clear_json_loader_opens_only_the_explicit_path(tmp_path: Path, monkeypatch) -> None:
    explicit_file = tmp_path / "target.clear.json"
    explicit_payload = {
        "case_id": "explicit_only",
        "table_id": "table_01",
        "hand_id": "hand_01",
        "hero_cards": ["As", "Kd"],
    }
    explicit_file.write_text(json.dumps(explicit_payload), encoding="utf-8")

    for name in (
        "nearby.dark_json.json",
        "nearby.pending_json.json",
        "nearby.service_json.json",
        "nearby.runtime_json.json",
    ):
        (tmp_path / name).write_text(json.dumps({"case_id": name}), encoding="utf-8")

    opened_paths: list[Path] = []
    original_open = Path.open

    def guarded_open(self: Path, *args, **kwargs):
        opened_paths.append(self.resolve())
        assert self.resolve() == explicit_file.resolve()
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)

    loaded = load_clear_json_input(explicit_file)

    assert loaded.case_id == "explicit_only"
    assert opened_paths == [explicit_file.resolve()]


def test_solver_input_build_does_not_read_any_files(tmp_path: Path, monkeypatch) -> None:
    payload = {
        "case_id": "no_file_reads",
        "table_id": "table_02",
        "hand_id": "hand_02",
        "hero_cards": ["Qh", "Qs"],
    }
    clear_input = ClearJsonInput(
        source_file=str(tmp_path / "already_loaded.clear.json"),
        raw_data=payload,
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id="no_file_reads",
        hand_id="hand_02",
        table_id="table_02",
    )

    def blocked_open(*args, **kwargs):
        raise AssertionError("build_solver_input must not open files")

    monkeypatch.setattr(Path, "open", blocked_open)

    solver_input, trace = build_solver_input(clear_input)

    assert solver_input.table_id == "table_02"
    assert trace.input_kind == "clear_json"


def test_solver_input_build_does_not_mutate_clear_json_payload() -> None:
    payload = {
        "case_id": "read_only_mapping",
        "table_id": "table_03",
        "hand_id": "hand_03",
        "players": [{"id": "hero", "stack": 100.0}],
        "allowed_actions": ["check", "bet"],
    }
    before = json.loads(json.dumps(payload))
    clear_input = ClearJsonInput(
        source_file="read_only_mapping.clear.json",
        raw_data=payload,
        loaded_at="2026-06-11T00:00:00+00:00",
        case_id="read_only_mapping",
        hand_id="hand_03",
        table_id="table_03",
    )

    build_solver_input(clear_input)

    assert payload == before


def test_no_poker_validation_symbols_are_exposed_by_public_package() -> None:
    import solver_postflop

    public_names = set(solver_postflop.__all__)
    forbidden_public_terms = (
        "validate",
        "validator",
        "duplicate",
        "collision",
        "filter",
        "fallback",
        "discovery",
    )

    for public_name in public_names:
        lowered = public_name.lower()
        for term in forbidden_public_terms:
            assert term not in lowered
