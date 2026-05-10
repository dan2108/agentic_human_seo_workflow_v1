from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class PhaseRef:
    id: str
    order: int
    name: str
    definition: str | Path
    output: str
    human_gate: str


@dataclass(frozen=True)
class WorkflowDefinition:
    id: str
    name: str
    phases: tuple[PhaseRef, ...]
    version: str | None = None
    source_image: str | Path | None = None
    objective: str | None = None
    shared_memory: Mapping[str, str] | None = None
    orchestration_principles: tuple[str, ...] = ()
    quality_bar: tuple[str, ...] = ()


@dataclass(frozen=True)
class PhaseDefinition:
    id: str
    name: str
    order: int
    objective: str
    inputs: tuple[str, ...]
    agents: tuple[str, ...]
    actions: tuple[str, ...]
    outputs: tuple[str, ...]
    quality_gate: str
    human_gate: str
    handoff: str

