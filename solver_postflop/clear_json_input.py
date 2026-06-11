"""Explicit Clear JSON loader for the postflop solver layer."""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Union

from solver_postflop.engine_contracts import ClearJsonInput

PathLike = Union[str, Path]

_ID_KEYS = {
    "case_id": ("case_id", "caseId"),
    "hand_id": ("hand_id", "handId", "hand"),
    "table_id": ("table_id", "tableId", "table"),
}

_METADATA_KEYS = ("metadata", "meta", "clear_json_metadata")


def load_clear_json_input(path: PathLike) -> ClearJsonInput:
    """Load one explicitly supplied Clear JSON file as trusted solver input."""

    source_path = Path(path)
    with source_path.open("r", encoding="utf-8") as file_obj:
        loaded_data = json.load(file_obj)

    if not isinstance(loaded_data, dict):
        raise TypeError("Clear JSON root must be a JSON object.")

    raw_data = copy.deepcopy(loaded_data)

    return ClearJsonInput(
        source_file=str(source_path),
        raw_data=raw_data,
        loaded_at=datetime.now(timezone.utc).isoformat(),
        case_id=_extract_optional_id(raw_data, "case_id"),
        hand_id=_extract_optional_id(raw_data, "hand_id"),
        table_id=_extract_optional_id(raw_data, "table_id"),
    )


def _extract_optional_id(raw_data: Mapping[str, Any], field_name: str) -> Optional[str]:
    for key in _ID_KEYS[field_name]:
        value = raw_data.get(key)
        if value not in (None, ""):
            return str(value)

    for container_key in _METADATA_KEYS:
        container = raw_data.get(container_key)
        if not isinstance(container, Mapping):
            continue
        for key in _ID_KEYS[field_name]:
            value = container.get(key)
            if value not in (None, ""):
                return str(value)

    return None
