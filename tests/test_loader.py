import sys
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from workflow_runner.loader import load_phase_definition, load_workflow


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


def test_load_workflow_reads_phase_order(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow" / "workflow.yaml"
    _write(
        workflow_path,
        """
        id: agentic-premium-website-workflow
        name: Agentic Workflow
        phases:
          - id: workflow-foundation
            order: 0
            name: Workflow Foundation
            definition: phases/00-workflow-foundation.yaml
            output: Workflow foundation package
            human_gate: Workflow readiness approval
          - id: intake-onboarding
            order: 1
            name: Intake & Onboarding
            definition: phases/01-intake-onboarding.yaml
            output: Approved brief and project data
            human_gate: Brief approval
          - id: research-planning
            order: 2
            name: Research & Planning
            definition: phases/02-research-planning.yaml
            output: Strategy document and sitemap
            human_gate: Strategy approval
          - id: design-content
            order: 3
            name: Design & Content Creation
            definition: phases/03-design-content.yaml
            output: Design files and content pack
            human_gate: Design approval
          - id: build-development
            order: 4
            name: Build & Development
            definition: phases/04-build-development.yaml
            output: Feature-complete staging website
            human_gate: Staging readiness review
          - id: qa-optimization
            order: 5
            name: QA & Optimization
            definition: phases/05-qa-optimization.yaml
            output: Optimized approved website
            human_gate: Launch approval
          - id: deploy-launch
            order: 6
            name: Deploy & Launch
            definition: phases/06-deploy-launch.yaml
            output: Live website
            human_gate: Production launch confirmation
          - id: monitor-iterate
            order: 7
            name: Monitor & Iterate
            definition: phases/07-monitor-iterate.yaml
            output: Post-launch report, ongoing cadence, and improved website
            human_gate: Iteration approval for material changes
        """,
    )

    workflow = load_workflow(workflow_path)

    assert [phase.id for phase in workflow.phases] == [
        "workflow-foundation",
        "intake-onboarding",
        "research-planning",
        "design-content",
        "build-development",
        "qa-optimization",
        "deploy-launch",
        "monitor-iterate",
    ]
    assert [phase.order for phase in workflow.phases] == list(range(8))


def test_load_phase_definition_returns_expected_inputs(tmp_path: Path) -> None:
    phase_path = tmp_path / "workflow" / "phases" / "05-qa-optimization.yaml"
    _write(
        phase_path,
        """
        id: qa-optimization
        name: QA & Optimization
        order: 5
        objective: Validate staging quality across functionality, content, devices, accessibility, SEO, performance, and launch readiness.
        inputs:
          - Phase 05 QA handoff package and staging readiness review
          - Feature-complete staging website with staging URL, Source Control branch, Commit reference, routes, key user flows, forms, CMS editing areas, integrations, analytics events, known issues, accepted risks, and deferred scope
        agents:
          - ../agents/qa-testing-agent.yaml
          - ../agents/performance-agent.yaml
        actions:
          - Confirm Phase 05 QA handoff package and staging readiness review are complete.
        outputs:
          - QA test plan
          - Functional QA report
          - Optimized approved website
          - Launch readiness review
          - Phase 06 launch handoff package
        quality_gate: Critical functionality works and launch-blocking issues are resolved.
        human_gate: Launch approval
        handoff: deploy-launch
        """,
    )

    phase = load_phase_definition(phase_path)

    assert phase.id == "qa-optimization"
    assert "staging readiness review" in phase.inputs[0]
    assert phase.handoff == "deploy-launch"
