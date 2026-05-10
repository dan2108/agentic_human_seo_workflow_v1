from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class AgentRequest:
    repo_root: Path
    project_root: Path
    workflow_id: str
    workflow_name: str
    phase_id: str
    phase_name: str
    phase_order: int
    phase_definition: str
    phase_output: str
    human_gate: str
    requested_outputs: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class AgentResult:
    phase_id: str
    status: str
    blockers: list[str] = field(default_factory=list)
    next_action: str = ""
    outputs: list[Path] = field(default_factory=list)
    note: str = ""


@runtime_checkable
class AgentRouter(Protocol):
    def route(self, request: AgentRequest) -> AgentResult:
        raise NotImplementedError


class LocalCodexAgentRouter:
    def route(self, request: AgentRequest) -> AgentResult:
        project_root = request.project_root.resolve()
        blockers: list[str] = []
        outputs: list[Path] = []

        for requested_output in request.requested_outputs:
            output_path = self._resolve_requested_output(project_root, requested_output)
            if output_path is None:
                blockers.append(
                    f"Requested output {requested_output!s} escapes outside the project workspace."
                )
                continue

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(self._render_output(request), encoding="utf-8")
            outputs.append(output_path)

        if blockers:
            return AgentResult(
                phase_id=request.phase_id,
                status="blocked",
                blockers=blockers,
                next_action="Resolve unsafe output paths and retry.",
                outputs=outputs,
                note="Local router refused to write paths outside the project workspace.",
            )

        return AgentResult(
            phase_id=request.phase_id,
            status="complete",
            outputs=outputs,
            note="Local router completed deterministically without invoking subagents.",
        )

    def _resolve_requested_output(self, project_root: Path, requested_output: Path) -> Path | None:
        candidate = requested_output if requested_output.is_absolute() else project_root / requested_output
        resolved_candidate = candidate.resolve()

        try:
            resolved_candidate.relative_to(project_root)
        except ValueError:
            return None

        return resolved_candidate

    def _render_output(self, request: AgentRequest) -> str:
        return (
            f"workflow_id: {request.workflow_id}\n"
            f"workflow_name: {request.workflow_name}\n"
            f"phase_id: {request.phase_id}\n"
            f"phase_name: {request.phase_name}\n"
            f"phase_order: {request.phase_order}\n"
            f"phase_definition: {request.phase_definition}\n"
            f"phase_output: {request.phase_output}\n"
            f"human_gate: {request.human_gate}\n"
        )
