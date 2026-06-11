"""Trace helpers for the versioned Clear JSON field mapping contract.

The functions here are reporting utilities. They inspect an already loaded
ClearJsonInput and an already built SolverInput, then explain how the mapping
contract applies to that pair. They do not repair poker data or choose poker
actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from solver_postflop.engine_contracts import ClearJsonInput, SolverInput
from solver_postflop.field_mapping_contract import (
    CLEAR_JSON_FIELD_MAPPINGS,
    FIELD_MAPPING_VERSION,
    ClearJsonFieldRequirement,
    FieldMappingEntry,
    FutureSolverModule,
    clear_json_fields_in_contract,
)


class FieldUsageStatus(str, Enum):
    """Status assigned to a mapping entry for one Clear JSON payload."""

    USED = "used"
    NOT_PROVIDED = "not_provided"
    IGNORED = "ignored"


@dataclass(frozen=True)
class FieldUsageRecord:
    """One trace row linked back to a FieldMappingEntry."""

    clear_json_fields: tuple[str, ...]
    solver_input_field: str
    requirement: ClearJsonFieldRequirement
    future_modules: tuple[FutureSolverModule, ...]
    status: FieldUsageStatus
    note: str

    @classmethod
    def from_mapping(
        cls,
        entry: FieldMappingEntry,
        status: FieldUsageStatus,
        note: str,
    ) -> "FieldUsageRecord":
        """Create a trace row from a mapping contract entry."""

        return cls(
            clear_json_fields=entry.clear_json_fields,
            solver_input_field=entry.solver_input_field,
            requirement=entry.requirement,
            future_modules=entry.future_modules,
            status=status,
            note=note,
        )

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of this record."""

        return {
            "clear_json_fields": list(self.clear_json_fields),
            "solver_input_field": self.solver_input_field,
            "requirement": self.requirement.value,
            "future_modules": [module.value for module in self.future_modules],
            "status": self.status.value,
            "note": self.note,
        }


@dataclass(frozen=True)
class FieldUsageTrace:
    """Full trace of contract field usage for one SolverInput build."""

    case_id: str | None
    source_file: str
    mapping_version: str
    fields_used: tuple[str, ...] = field(default_factory=tuple)
    fields_not_provided: tuple[str, ...] = field(default_factory=tuple)
    fields_ignored: tuple[str, ...] = field(default_factory=tuple)
    future_modules_enabled: tuple[str, ...] = field(default_factory=tuple)
    records: tuple[FieldUsageRecord, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of this trace."""

        return {
            "case_id": self.case_id,
            "source_file": self.source_file,
            "mapping_version": self.mapping_version,
            "fields_used": list(self.fields_used),
            "fields_not_provided": list(self.fields_not_provided),
            "fields_ignored": list(self.fields_ignored),
            "future_modules_enabled": list(self.future_modules_enabled),
            "records": [record.to_json_dict() for record in self.records],
            "notes": list(self.notes),
        }


def build_field_usage_trace(
    clear_input: ClearJsonInput,
    solver_input: SolverInput,
) -> FieldUsageTrace:
    """Build a contract-backed report for one Clear JSON to SolverInput pair."""

    raw_data = clear_input.raw_data
    if not isinstance(raw_data, Mapping):
        raise TypeError("ClearJsonInput.raw_data must be a mapping.")

    fields_used: list[str] = []
    fields_not_provided: list[str] = []
    enabled_modules: list[str] = []
    records: list[FieldUsageRecord] = []

    for entry in CLEAR_JSON_FIELD_MAPPINGS:
        matched_source_fields = tuple(field for field in entry.clear_json_fields if field in raw_data)
        if matched_source_fields:
            fields_used.append(entry.solver_input_field)
            enabled_modules.extend(module.value for module in entry.future_modules)
            records.append(
                FieldUsageRecord.from_mapping(
                    entry,
                    FieldUsageStatus.USED,
                    f"provided_by:{','.join(matched_source_fields)}",
                )
            )
        else:
            fields_not_provided.append(entry.solver_input_field)
            records.append(
                FieldUsageRecord.from_mapping(
                    entry,
                    FieldUsageStatus.NOT_PROVIDED,
                    "source_field_not_present_in_clear_json",
                )
            )

    ignored_fields = _ignored_clear_json_fields(raw_data)
    for field_name in ignored_fields:
        records.append(
            FieldUsageRecord(
                clear_json_fields=(field_name,),
                solver_input_field="",
                requirement=ClearJsonFieldRequirement.OPTIONAL_NOT_PROVIDED_ALLOWED,
                future_modules=(),
                status=FieldUsageStatus.IGNORED,
                note="clear_json_field_not_described_by_contract",
            )
        )

    notes = [
        "field usage trace is contract-backed and report-only",
        "SolverInput.raw_clear_json_ref remains attached to the original Clear JSON object"
        if solver_input.raw_clear_json_ref is raw_data
        else "SolverInput.raw_clear_json_ref does not point to the original Clear JSON object",
    ]

    return FieldUsageTrace(
        case_id=clear_input.case_id,
        source_file=clear_input.source_file,
        mapping_version=FIELD_MAPPING_VERSION,
        fields_used=tuple(_dedupe_preserve_order(fields_used)),
        fields_not_provided=tuple(_dedupe_preserve_order(fields_not_provided)),
        fields_ignored=ignored_fields,
        future_modules_enabled=tuple(_dedupe_preserve_order(enabled_modules)),
        records=tuple(records),
        notes=tuple(notes),
    )


def _ignored_clear_json_fields(raw_data: Mapping[str, Any]) -> tuple[str, ...]:
    described = set(clear_json_fields_in_contract())
    return tuple(sorted(field_name for field_name in raw_data if field_name not in described))


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
