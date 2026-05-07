# State Diagram: To-Be — Agentic Human SEO Workflow with UI Layer

```mermaid
stateDiagram-v2
    [*] --> OnboardingForm: human opens Next.js app

    state OnboardingForm {
        [*] --> FillingForm
        FillingForm --> FormSubmitted: submit
    }

    FormSubmitted --> PipelineView: job created in Supabase

    state PipelineView {
        [*] --> ShowingJobStatus
        ShowingJobStatus --> GatePulsing: gate awaiting human
        GatePulsing --> GateReviewOpen: human clicks gate node
    }

    state AuditAgentsRunning {
        [*] --> CrawlAgent
        CrawlAgent --> TechAgent
        TechAgent --> ContentAuditAgent
        ContentAuditAgent --> SynthesisAgent
        SynthesisAgent --> AuditReportReady
    }

    FormSubmitted --> AuditAgentsRunning: FastAPI job dispatched
    AuditAgentsRunning --> PipelineView: Realtime status update

    state Gate1Review {
        [*] --> ViewingAuditReport
        ViewingAuditReport --> PrioritizingBacklog: drag to reorder
        PrioritizingBacklog --> Gate1Decision
    }

    state Gate1Decision <<choice>>
    Gate1Review --> Gate1Decision
    Gate1Decision --> ResearchAgentsRunning: approved
    Gate1Decision --> Gate1Review: rejected - revise

    state ResearchAgentsRunning {
        [*] --> KeywordAgent
        KeywordAgent --> IntentAgent
        IntentAgent --> StrategyAgent
        StrategyAgent --> CalendarReady
    }

    ResearchAgentsRunning --> TechFixAgentsRunning: parallel
    ResearchAgentsRunning --> PipelineView: Realtime update

    state TechFixAgentsRunning {
        [*] --> SchemaAgent
        SchemaAgent --> MetaAgent
        MetaAgent --> TechFixComplete
    }

    CalendarReady --> PipelineView: Gate 2 pending

    state Gate2Review {
        [*] --> ViewingCalendar
        ViewingCalendar --> Gate2Decision
    }

    state Gate2Decision <<choice>>
    Gate2Review --> Gate2Decision
    Gate2Decision --> ContentEditorOpen: approved
    Gate2Decision --> ResearchAgentsRunning: revise strategy

    state ContentEditorOpen {
        [*] --> BriefLoaded
        BriefLoaded --> WritingContent: human writes in TipTap
        WritingContent --> AICopilotAssisting: co-pilot active
        AICopilotAssisting --> WritingContent: human continues
        WritingContent --> DraftSaved: auto-save to Supabase
        DraftSaved --> QAAgentsRunning
    }

    state QAAgentsRunning {
        [*] --> VoiceCheck
        VoiceCheck --> PlagiarismCheck
        PlagiarismCheck --> QAComplete
    }

    TechFixAgentsRunning --> QAAgentsRunning: parallel merge
    QAAgentsRunning --> PipelineView: Gate 3 pending

    state Gate3Review {
        [*] --> SideBySidePreview
        SideBySidePreview --> QAAnnotationsVisible
        QAAnnotationsVisible --> Gate3Decision
    }

    state Gate3Decision <<choice>>
    Gate3Review --> Gate3Decision
    Gate3Decision --> PublishAgentsReady: pass
    Gate3Decision --> ContentEditorOpen: fail - revise

    PublishAgentsReady --> PipelineView: Gate 4 pending

    state Gate4Confirm {
        [*] --> OneClickConfirm
        OneClickConfirm --> PublishAgentsRunning
    }

    state PublishAgentsRunning {
        [*] --> CMSPushAgent
        CMSPushAgent --> InternalLinkAgent
        InternalLinkAgent --> IndexPingAgent
        IndexPingAgent --> SocialDraftAgent
        SocialDraftAgent --> PublishComplete
    }

    PublishAgentsRunning --> BaselineSnapshotAgent
    PublishAgentsRunning --> MonitorAgentRunning: parallel

    state AftercareRunning {
        [*] --> Day7Agent
        Day7Agent --> Day7Triage
        Day7Triage --> Day30Agent: clear
        Day7Triage --> AutoFixAttempt: issues
        AutoFixAttempt --> Day30Agent
        Day30Agent --> Day90Agent
        Day90Agent --> ClassificationEngine
    }

    BaselineSnapshotAgent --> AftercareRunning

    state AftercareRunning {
        ClassificationEngine --> OutcomeRouting
    }

    state OutcomeRouting <<choice>>
    OutcomeRouting --> RepurposeFlow: winner
    OutcomeRouting --> MonitorAgentRunning: steady
    OutcomeRouting --> ContentEditorOpen: underperformer refresh
    OutcomeRouting --> DeprecateAction: loser

    AftercareRunning --> AftercareDashboard: Realtime update
    MonitorAgentRunning --> Aftercaredashboard: alerts

    state AftercareDashboard {
        [*] --> ViewingDay7Tab
        ViewingDay7Tab --> ViewingDay30Tab
        ViewingDay30Tab --> ViewingDay90Tab
        ViewingDay90Tab --> ViewingOutcomeBadge
    }

    RepurposeFlow --> ContentEditorOpen: new brief
    DeprecateAction --> [*]: 301 or noindex applied
```
