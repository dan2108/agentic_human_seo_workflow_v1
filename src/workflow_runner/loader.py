from pathlib import Path
from typing import Any

import yaml

from .models import PhaseDefinition, PhaseRef, WorkflowDefinition


def _load_yaml(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def _as_tuple(values: Any) -> tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(value) for value in values)


def load_workflow(path: str | Path) -> WorkflowDefinition:
    data = _load_yaml(path)
    phases = tuple(
        sorted(
            (
                PhaseRef(
                    id=str(phase["id"]),
                    order=int(phase["order"]),
                    name=str(phase["name"]),
                    definition=phase["definition"],
                    output=str(phase["output"]),
                    human_gate=str(phase["human_gate"]),
                )
                for phase in data.get("phases", [])
            ),
            key=lambda phase: phase.order,
        )
    )
    shared_memory = data.get("shared_memory")
    if shared_memory is not None and not isinstance(shared_memory, dict):
        raise ValueError("shared_memory must be a mapping")
    return WorkflowDefinition(
        id=str(data["id"]),
        name=str(data["name"]),
        phases=phases,
        version=None if data.get("version") is None else str(data["version"]),
        source_image=data.get("source_image"),
        objective=None if data.get("objective") is None else str(data["objective"]),
        shared_memory=shared_memory,
        orchestration_principles=_as_tuple(data.get("orchestration_principles")),
        quality_bar=_as_tuple(data.get("quality_bar")),
    )


def load_phase_definition(path: str | Path) -> PhaseDefinition:
    data = _load_yaml(path)
    return PhaseDefinition(
        id=str(data["id"]),
        name=str(data["name"]),
        order=int(data["order"]),
        objective=str(data["objective"]),
        inputs=_as_tuple(data.get("inputs")),
        agents=_as_tuple(data.get("agents")),
        actions=_as_tuple(data.get("actions")),
        outputs=_as_tuple(data.get("outputs")),
        quality_gate=str(data["quality_gate"]),
        human_gate=str(data["human_gate"]),
        handoff=str(data["handoff"]),
    )
