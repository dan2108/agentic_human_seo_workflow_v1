from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from workflow_runner.agent_router import AgentRequest, AgentResult, LocalCodexAgentRouter


def test_agent_request_captures_phase_metadata() -> None:
    request = AgentRequest(
        repo_root=Path(r"C:\Users\danie\website_workflow"),
        project_root=Path(r"C:\Users\danie\sample_website"),
        workflow_id="agentic-premium-website-workflow",
        workflow_name="Agentic Workflow: Automated Premium Website Creation",
        phase_id="build-development",
        phase_name="Build & Development",
        phase_order=4,
        phase_definition="phases/04-build-development.yaml",
        phase_output="Feature-complete staging website",
        human_gate="Staging readiness review",
        requested_outputs=[Path("phase-04-build-development") / "agent-output.md"],
    )

    assert request.phase_id == "build-development"
    assert request.workflow_id == "agentic-premium-website-workflow"


def test_local_router_returns_success_result_and_writes_requested_output(tmp_path: Path) -> None:
    router = LocalCodexAgentRouter()
    project_root = tmp_path / "sample_website"
    result = router.route(
        AgentRequest(
            repo_root=Path(r"C:\Users\danie\website_workflow"),
            project_root=project_root,
            workflow_id="agentic-premium-website-workflow",
            workflow_name="Agentic Workflow: Automated Premium Website Creation",
            phase_id="build-development",
            phase_name="Build & Development",
            phase_order=4,
            phase_definition="phases/04-build-development.yaml",
            phase_output="Feature-complete staging website",
            human_gate="Staging readiness review",
            requested_outputs=[Path("phase-04-build-development") / "agent-output.md"],
        )
    )

    assert result.status == "complete"
    assert result.phase_id == "build-development"
    assert result.blockers == []
    assert result.outputs
    assert all(output.exists() for output in result.outputs)
    assert all(project_root in output.parents or output == project_root for output in result.outputs)


def test_local_router_blocks_unsafe_artifact_paths(tmp_path: Path) -> None:
    router = LocalCodexAgentRouter()
    result = router.route(
        AgentRequest(
            repo_root=Path(r"C:\Users\danie\website_workflow"),
            project_root=tmp_path / "sample_website",
            workflow_id="agentic-premium-website-workflow",
            workflow_name="Agentic Workflow: Automated Premium Website Creation",
            phase_id="build-development",
            phase_name="Build & Development",
            phase_order=4,
            phase_definition="phases/04-build-development.yaml",
            phase_output="Feature-complete staging website",
            human_gate="Staging readiness review",
            requested_outputs=[Path("..") / "escape.md"],
        )
    )

    assert result.status == "blocked"
    assert result.blockers
    assert "outside the project workspace" in result.blockers[0]
