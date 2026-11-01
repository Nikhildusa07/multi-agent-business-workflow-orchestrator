import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getWorkflow,
  getAuditLogs,
} from "../services/api";

const workflowSteps = [
  {
    key: "INTAKE",
    label: "Intake",
    description: "Request classification",
  },
  {
    key: "PLANNING",
    label: "Planning",
    description: "Task planning",
  },
  {
    key: "EXECUTION",
    label: "Execution",
    description: "Task execution",
  },
  {
    key: "REVIEW",
    label: "Review",
    description: "Quality validation",
  },
  {
    key: "COMPLETED",
    label: "Completed",
    description: "Workflow finished",
  },
];

function WorkflowDetails() {
  const { workflowId } = useParams();

  const [workflow, setWorkflow] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);

        const workflowResponse =
          await getWorkflow(workflowId);

        setWorkflow(workflowResponse.data);

        const logsResponse =
          await getAuditLogs();

        const workflowLogs =
          Array.isArray(logsResponse.data)
            ? logsResponse.data.filter(
                (log) =>
                  log.workflow_id === Number(workflowId)
              )
            : [];

        setLogs(workflowLogs);
      } catch (error) {
        console.error(
          "Failed to load workflow:",
          error
        );
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [workflowId]);

  if (loading) {
    return (
      <div className="page-container">
        <div className="workflow-details-loading">
          <div className="workflow-loading-spinner">
            ⟳
          </div>

          <h3>Loading workflow...</h3>

          <p>
            Fetching workflow details and activity history.
          </p>
        </div>
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="page-container">
        <div className="workflow-details-empty">
          <div className="workflow-empty-icon">!</div>

          <h3>Workflow not found</h3>

          <p>
            The requested workflow could not be loaded.
          </p>

          <Link
            to="/workflows"
            className="primary-button"
          >
            Back to Workflows
          </Link>
        </div>
      </div>
    );
  }

  const normalizedStatus = String(
    workflow.status || "UNKNOWN"
  ).toUpperCase();

  const normalizedState = String(
    workflow.current_state || "PENDING"
  ).toUpperCase();

  const currentStepIndex = workflowSteps.findIndex(
    (step) => step.key === normalizedState
  );

  const getStepClass = (index) => {
    if (normalizedStatus === "FAILED") {
      if (index < currentStepIndex) {
        return "completed";
      }

      if (index === currentStepIndex) {
        return "failed";
      }

      return "";
    }

    if (
      normalizedStatus === "COMPLETED" ||
      index < currentStepIndex
    ) {
      return "completed";
    }

    if (index === currentStepIndex) {
      return "active";
    }

    return "";
  };

  const getLogStatusClass = (status) => {
    const value = String(status || "")
      .toLowerCase()
      .replace(/\s+/g, "-");

    return `detail-log-status ${value}`;
  };

  const getStatusIcon = (status) => {
    const value = String(status || "").toUpperCase();

    if (
      value === "COMPLETED" ||
      value === "SUCCESS" ||
      value === "APPROVED"
    ) {
      return "✓";
    }

    if (
      value === "FAILED" ||
      value === "ERROR"
    ) {
      return "!";
    }

    if (
      value === "RUNNING" ||
      value === "RETRYING"
    ) {
      return "↻";
    }

    return "•";
  };

  return (
    <div className="page-container workflow-details-page">

      {/* HEADER */}
      <div className="workflow-details-header">

        <div>
          <Link
            to="/workflows"
            className="back-link workflow-details-back"
          >
            ← Back to Workflows
          </Link>

          <div className="workflow-details-eyebrow">
            WORKFLOW DETAILS
          </div>

          <div className="workflow-title-row">
            <div>
              <h1>{workflow.workflow_name}</h1>

              <p>
                Workflow #{workflow.id}
              </p>
            </div>

            <span
              className={`workflow-detail-status status-${normalizedStatus.toLowerCase()}`}
            >
              <span className="workflow-detail-status-dot" />
              {normalizedStatus}
            </span>
          </div>
        </div>

      </div>

      {/* WORKFLOW PROGRESS */}
      <section className="workflow-detail-panel">

        <div className="workflow-detail-panel-header">
          <div>
            <span className="workflow-panel-eyebrow">
              ORCHESTRATION
            </span>

            <h2>Workflow Progress</h2>

            <p>
              Track the workflow as it moves through
              each AI agent.
            </p>
          </div>

          <div className="current-state-pill">
            Current state:
            <strong>{normalizedState}</strong>
          </div>
        </div>

        <div className="workflow-progress">

          {workflowSteps.map((step, index) => {
            const stepClass = getStepClass(index);

            return (
              <div
                className={`workflow-progress-step ${stepClass}`}
                key={step.key}
              >

                <div className="workflow-step-marker">
                  {stepClass === "completed"
                    ? "✓"
                    : stepClass === "failed"
                    ? "!"
                    : index + 1}
                </div>

                <div className="workflow-step-content">
                  <strong>{step.label}</strong>

                  <span>
                    {step.description}
                  </span>
                </div>

                {index <
                  workflowSteps.length - 1 && (
                  <div
                    className={`workflow-step-line ${
                      index < currentStepIndex
                        ? "completed"
                        : ""
                    }`}
                  />
                )}

              </div>
            );
          })}

        </div>

      </section>

      {/* REQUEST + METADATA */}
      <div className="workflow-detail-two-column">

        <section className="workflow-detail-panel">

          <div className="workflow-detail-panel-header compact">
            <div>
              <span className="workflow-panel-eyebrow">
                INPUT
              </span>

              <h2>Business Request</h2>

              <p>
                The request submitted to the orchestrator.
              </p>
            </div>
          </div>

          <div className="workflow-request-box">

            <div className="workflow-request-icon">
              ?
            </div>

            <div>
              <span>REQUEST</span>

              <p>
                {workflow.input_data?.request ||
                  "No request provided."}
              </p>
            </div>

          </div>

        </section>

        <section className="workflow-detail-panel">

          <div className="workflow-detail-panel-header compact">
            <div>
              <span className="workflow-panel-eyebrow">
                CONFIGURATION
              </span>

              <h2>Workflow Information</h2>

              <p>
                Current workflow configuration.
              </p>
            </div>
          </div>

          <div className="workflow-info-grid">

            <div className="workflow-info-item">
              <span>Workflow ID</span>
              <strong>#{workflow.id}</strong>
            </div>

            <div className="workflow-info-item">
              <span>Priority</span>
              <strong>
                {String(
                  workflow.input_data?.priority ||
                    "normal"
                ).toUpperCase()}
              </strong>
            </div>

            <div className="workflow-info-item">
              <span>Status</span>
              <strong>{normalizedStatus}</strong>
            </div>

            <div className="workflow-info-item">
              <span>Current State</span>
              <strong>{normalizedState}</strong>
            </div>

          </div>

        </section>

      </div>

      {/* ACTIVITY */}
      <section className="workflow-detail-panel">

        <div className="workflow-detail-panel-header">

          <div>
            <span className="workflow-panel-eyebrow">
              OBSERVABILITY
            </span>

            <h2>Workflow Activity</h2>

            <p>
              Complete execution history from the
              workflow agents and system.
            </p>
          </div>

          <div className="activity-count">
            {logs.length}
            <span>events</span>
          </div>

        </div>

        {logs.length === 0 ? (
          <div className="workflow-activity-empty">

            <div className="workflow-empty-icon">
              +
            </div>

            <strong>
              No activity recorded
            </strong>

            <span>
              Activity will appear here when the
              workflow starts executing.
            </span>

          </div>
        ) : (
          <div className="workflow-activity-list">

            {logs.map((log) => (

              <div
                className="workflow-activity-item"
                key={log.id}
              >

                <div className="activity-icon">
                  {getStatusIcon(log.status)}
                </div>

                <div className="activity-main">

                  <div className="activity-title-row">

                    <div>
                      <strong>
                        {log.action
                          ?.replace(/_/g, " ")
                          .replace(/\b\w/g, (letter) =>
                            letter.toUpperCase()
                          ) ||
                          "Workflow Activity"}
                      </strong>

                      <span className="activity-agent">
                        {log.agent}
                      </span>
                    </div>

                    <span
                      className={getLogStatusClass(
                        log.status
                      )}
                    >
                      {String(
                        log.status || "UNKNOWN"
                      ).toUpperCase()}
                    </span>

                  </div>

                  <p>
                    {log.message ||
                      "No additional information provided."}
                  </p>

                  <div className="activity-meta">

                    <span>
                      Event #{log.id}
                    </span>

                    <span>•</span>

                    <span>
                      {log.timestamp
                        ? new Date(
                            log.timestamp
                          ).toLocaleString()
                        : "Unknown time"}
                    </span>

                  </div>

                </div>

              </div>

            ))}

          </div>
        )}

      </section>

    </div>
  );
}

export default WorkflowDetails;