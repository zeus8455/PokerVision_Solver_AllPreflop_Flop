import json
from pathlib import Path

import pytest

from solver_postflop.contracts import (
    ContractSeverity,
    ContractValidationError,
    ModuleError,
    ModuleWarning,
    PostflopSourceType,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "tests" / "fixtures" / "postflop" / "manifest.json"


def test_v031_source_types_match_v020_fixture_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert PostflopSourceType.values() == manifest["allowed_source_types"]


def test_v031_source_type_accepts_only_explicit_allowed_values():
    assert PostflopSourceType.from_value("dark_json") is PostflopSourceType.DARK_JSON
    assert PostflopSourceType.from_value(PostflopSourceType.UNKNOWN) is PostflopSourceType.UNKNOWN

    with pytest.raises(ContractValidationError):
        PostflopSourceType.from_value("clear_json_pending")


def test_v031_final_clear_json_is_supported_but_not_required():
    assert "final_clear_json" in PostflopSourceType.values()
    assert PostflopSourceType.FINAL_CLEAR_JSON.requires_click_cycle_by_type is True

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_case_source_types = {case["source_type"] for case in manifest["cases"]}

    assert manifest["rules"]["final_clear_json_required"] is False
    assert manifest_case_source_types == {"dark_json"}


def test_v031_manual_live_like_type_is_not_real_project_source():
    manual_type = PostflopSourceType.MANUAL_LIVE_LIKE_JSON

    assert manual_type.is_manual_live_like is True
    assert manual_type.can_be_real_project_source is False
    assert PostflopSourceType.UNKNOWN.can_be_real_project_source is False
    assert PostflopSourceType.DARK_JSON.can_be_real_project_source is True


def test_v031_module_warning_is_structured_and_json_serializable():
    warning = ModuleWarning(
        code="missing_table_id",
        message="table_id is not present in source JSON.",
        severity="warning",
        source_file="tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
        field_name="table_id",
        context={"source_type": "dark_json"},
    )

    payload = warning.to_dict()

    assert payload == {
        "code": "missing_table_id",
        "message": "table_id is not present in source JSON.",
        "severity": "warning",
        "source_file": "tests/fixtures/postflop/source_json/dark_json/flop_source_case_001.dark.json",
        "field_name": "table_id",
        "context": {"source_type": "dark_json"},
    }
    json.dumps(payload)


def test_v031_module_warning_rejects_empty_code_or_error_severity():
    with pytest.raises(ContractValidationError):
        ModuleWarning(code="", message="message")

    with pytest.raises(ContractValidationError):
        ModuleWarning(code="bad", message="message", severity=ContractSeverity.ERROR)


def test_v031_module_error_is_structured_and_json_serializable():
    error = ModuleError(
        code="invalid_source_type",
        message="source_type is unsupported.",
        source_file="bad.json",
        field_name="source_type",
        context={"received": "not_a_source"},
    )

    payload = error.to_dict()

    assert payload["severity"] == "error"
    assert payload["is_fatal"] is True
    assert payload["context"] == {"received": "not_a_source"}
    json.dumps(payload)


def test_v031_module_error_rejects_non_error_severity():
    with pytest.raises(ContractValidationError):
        ModuleError(code="bad", message="message", severity=ContractSeverity.WARNING)
