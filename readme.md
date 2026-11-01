# 🧠 Multi-Agent Business Workflow Orchestrator

### **What if AI agents didn't just answer a request — but actually operated a business workflow?**

Most AI-agent projects demonstrate a simple pattern:

> User → Agent → Response

This project explores a different question:

> **What happens when AI agents have responsibilities, ownership, permissions, approvals, failures, retries, memory, and accountability?**

The **Multi-Agent Business Workflow Orchestrator** is a backend orchestration system that coordinates specialized AI agents through a controlled business workflow.

Instead of allowing agents to act independently, every workflow moves through explicit states:

```text
                    ┌─────────────────┐
                    │   USER REQUEST  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ INTAKE AGENT    │
                    │ Understand      │
                    │ Classify        │
                    │ Prioritize      │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ PLANNING AGENT  │
                    │ Decompose       │
                    │ Assign          │
                    │ Define actions  │
                    └────────┬────────┘
                             ↓
                 ┌───────────┴───────────┐
                 ↓                       ↓
          ┌──────────────┐        ┌──────────────┐
          │   APPROVAL   │        │   EXECUTION  │
          │ Human Gate   │        │ Agent Tasks  │
          └──────┬───────┘        └──────┬───────┘
                 │                       │
                 └───────────┬───────────┘
                             ↓
                    ┌─────────────────┐
                    │  REVIEW AGENT   │
                    │ Validate result │
                    │ Quality check    │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │    COMPLETED    │
                    └─────────────────┘
```

But the interesting part is not the diagram.

The interesting part is **what happens when something goes wrong.**

---

# 🚨 The Problem

Real business workflows are not:

```text
Request → AI → Done
```

They look more like:

```text
Request
   ↓
Interpretation
   ↓
Planning
   ↓
Multiple tasks
   ↓
Something fails
   ↓
Retry
   ↓
Something requires approval
   ↓
Human decision
   ↓
Continue
   ↓
Review
   ↓
Audit
   ↓
Completion
```

A production-oriented agent system therefore needs more than intelligent responses.

It needs **control**.

This project was designed around that principle:

> ### **Agents provide intelligence. The orchestrator provides control.**

---

# 🎯 Core Idea

The system treats AI agents like specialized business departments.

| Agent | Responsibility |
|---|---|
| 🧾 Intake Agent | Understand and classify incoming requests |
| 🧠 Planning Agent | Convert requests into executable tasks |
| ⚙️ Execution Agent | Perform bounded business actions |
| 🔍 Review Agent | Validate execution results |
| 👤 Human | Approve consequential actions |

The orchestrator sits between them and controls:

- State transitions
- Task ownership
- Retry limits
- Human approval
- Failure handling
- Recovery
- Audit history
- Observability

This creates a workflow where agents **cannot simply jump from idea to action**.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │     API Gateway     │
                         └──────────┬──────────┘
                                    │
                                    ↓
                         ┌─────────────────────┐
                         │ Workflow Service    │
                         └──────────┬──────────┘
                                    │
                                    ↓
                    ┌───────────────────────────────┐
                    │       LangGraph Engine        │
                    │                               │
                    │  PENDING                     │
                    │     ↓                        │
                    │  INTAKE                      │
                    │     ↓                        │
                    │  PLANNING                    │
                    │     ↓                        │
                    │  EXECUTION ←─────┐           │
                    │     ↓             │           │
                    │  APPROVAL         │           │
                    │     ↓             │           │
                    │  REVIEW ──────────┘           │
                    │     ↓                        │
                    │  COMPLETED                   │
                    │                               │
                    │  or                          │
                    │     ↓                        │
                    │  FAILED                      │
                    └───────────────┬───────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ↓                     ↓                     ↓
       ┌─────────────┐       ┌─────────────┐      ┌─────────────┐
       │ PostgreSQL  │       │    Redis    │      │ OpenTelemetry│
       │             │       │             │      │             │
       │ Workflows   │       │ Checkpoints │      │ Traces      │
       │ Tasks       │       │ Recovery    │      │ Spans       │
       │ Approvals   │       │ State       │      │ Attributes  │
       │ Audit Logs  │       │             │      │             │
       └─────────────┘       └─────────────┘      └─────────────┘
```

---

# 🔄 The Workflow State Machine

The workflow is not allowed to move randomly between states.

```text
PENDING
   │
   ↓
INTAKE
   │
   ↓
PLANNING
   │
   ↓
EXECUTION ───────────────┐
   │                     │
   │ approval required   │ retry
   ↓                     │
APPROVAL                 │
   │                     │
   └────────→ EXECUTION ─┘
                 │
                 ↓
              REVIEW
                 │
          ┌──────┴──────┐
          ↓             ↓
      COMPLETED       FAILED
```

Invalid transitions are rejected by the orchestration layer.

This makes the workflow **state-aware rather than agent-driven chaos**.

---

# 🧩 Why LangGraph?

LangGraph provides the graph-based execution model required to represent a workflow where:

- Nodes represent processing stages
- State carries workflow information
- Conditional routing controls execution
- Execution can pause for approval
- Failed workflows can terminate safely
- Multiple tasks can be executed sequentially

The graph acts as the **control plane** for the agents.

---

# 🤖 Agent Responsibilities

## 1. Intake Agent

The first intelligence layer.

It converts an unstructured business request into structured information:

```json
{
  "success": true,
  "request": "Analyze our business performance",
  "category": "business_analysis",
  "priority": "normal"
}
```

It currently classifies requests into categories such as:

- `business_analysis`
- `communication`
- `customer_support`
- `general_business`

---

## 2. Planning Agent

The planner converts the classified request into executable tasks.

Example:

```text
Business Analysis
       ↓
Collect Data
       ↓
Analyze Performance
       ↓
Generate Report
```

Each task carries ownership and approval requirements.

Example:

```json
{
  "task_name": "Generate business report",
  "assigned_agent": "execution_agent",
  "action": "generate_report",
  "requires_approval": false
}
```

---

## 3. Execution Agent

The execution layer performs bounded actions.

Examples include:

```text
collect_data
analyze_data
generate_report
prepare_message
review_message
analyze_customer_request
prepare_response
execute_request
review_result
```

Execution is deliberately controlled by the orchestrator.

---

# 🔁 Bounded Retry System

Failures are expected.
