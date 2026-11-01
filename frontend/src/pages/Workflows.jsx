import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  createWorkflow,
  getWorkflows,
  runWorkflow,
} from "../services/api";

function Workflows() {
  const [workflows, setWorkflows] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    workflow_name: "",
    request: "",
    priority: "medium",
  });

  const loadWorkflows = async () => {
    try {
      setError("");

      const response = await getWorkflows();

      setWorkflows(
        Array.isArray(response.data)
          ? response.data
          : []
      );
    } catch (err) {
      console.error("Failed to load workflows:", err);
      setError("Unable to load workflows from the backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkflows();
  }, []);

  const statistics = useMemo(() => {
    const completed = workflows.filter(
      (workflow) =>
        String(workflow.status).toUpperCase() === "COMPLETED"
    ).length;

    const running = workflows.filter((workflow) =>
      ["RUNNING", "PENDING", "IN_PROGRESS"].includes(
        String(workflow.status).toUpperCase()
      )
    ).length;

    const failed = workflows.filter((workflow) =>
      ["FAILED", "ERROR"].includes(
        String(workflow.status).toUpperCase()
      )
    ).length;

    return {
      total: workflows.length,
      completed,
      running,
      failed,
    };
  }, [workflows]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (
      !form.workflow_name.trim() ||
      !form.request.trim()
    ) {
      setError(
        "Please enter both workflow name and business request."
      );
      return;
    }

    setCreating(true);
    setError("");

    try {
      const response = await createWorkflow({
        workflow_name: form.workflow_name.trim(),
        input_data: {
          request: form.request.trim(),
          priority: form.priority,
        },
      });

      const workflowId = response.data.id;

      await runWorkflow(workflowId);

      setForm({
        workflow_name: "",
        request: "",
        priority: "medium",
      });

      setShowForm(false);

      await loadWorkflows();
    } catch (err) {
      console.error("Workflow creation failed:", err);

      const message =
        err?.response?.data?.detail ||
        "Workflow could not be started.";

      setError(message);
    } finally {
      setCreating(false);
    }
  };

  const getStatusClass = (status) => {
    const normalized = String(status || "")
      .toLowerCase()
      .replace(/\s+/g, "-");

    return `workflow-status ${normalized}`;
  };

  const getStateLabel = (state) => {
    if (!state) {
      return "Unknown";
    }

    return String(state)
      .replace(/_/g, " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };

  return (
    <div className="page-container">
      {/* ============================================
          PAGE HEADER
      ============================================ */}
      <div className="page-header">
        <div>
          <p className="eyebrow">
            WORKFLOW MANAGEMENT
          </p>

          <h1>Workflows</h1>

          <p className="page-description">
            Create, execute and monitor AI-powered
            business workflows.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() =>
            setShowForm((previous) => !previous)
          }
        >
          {showForm ? "Close" : "+ New Workflow"}
        </button>
      </div>

      {/* ============================================
          ERROR
      ============================================ */}
      {error && (
        <div className="error-box">
          <span>{error}</span>

          <button
            type="button"
            onClick={() => setError("")}
          >
            ×
          </button>
        </div>
      )}

      {/* ============================================
          STATISTICS
      ============================================ */}
      <div className="workflow-summary-grid">
        <div className="workflow-summary-card">
          <span>Total Workflows</span>
          <strong>{statistics.total}</strong>
        </div>

        <div className="workflow-summary-card">
          <span>Completed</span>
          <strong>{statistics.completed}</strong>
        </div>

        <div className="workflow-summary-card">
          <span>Running</span>
          <strong>{statistics.running}</strong>
        </div>

        <div className="workflow-summary-card">
          <span>Failed</span>
          <strong>{statistics.failed}</strong>
        </div>
      </div>

      {/* ============================================
          CREATE WORKFLOW
      ============================================ */}
      {showForm && (
        <section className="dashboard-panel workflow-create-panel">
          <div className="panel-header">
            <div>
              <span className="panel-eyebrow">
                NEW AUTOMATION
              </span>

              <h2>Create Workflow</h2>

              <p>
                Describe the business task you want the
                AI agents to accomplish.
              </p>
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            className="workflow-form"
          >
            <div className="form-grid">
              <div className="form-field">
                <label htmlFor="workflow-name">
                  Workflow Name
                </label>

                <input
                  id="workflow-name"
                  type="text"
                  placeholder="Monthly Business Performance"
                  value={form.workflow_name}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      workflow_name:
                        event.target.value,
                    })
                  }
                />
              </div>

              <div className="form-field">
                <label htmlFor="workflow-priority">
                  Priority
                </label>

                <select
                  id="workflow-priority"
                  value={form.priority}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      priority: event.target.value,
                    })
                  }
                >
                  <option value="low">
                    Low
                  </option>

                  <option value="medium">
                    Medium
                  </option>

                  <option value="high">
                    High
                  </option>
                </select>
              </div>
            </div>

            <div className="form-field">
              <label htmlFor="business-request">
                Business Request
              </label>

              <textarea
                id="business-request"
                rows="5"
                placeholder="Create a business performance report and analyze profitability."
                value={form.request}
                onChange={(event) =>
                  setForm({
                    ...form,
                    request: event.target.value,
                  })
                }
              />
            </div>

            <div className="workflow-form-footer">
              <div className="workflow-flow-hint">
                <span>Intake</span>
                <span>→</span>
                <span>Planning</span>
                <span>→</span>
                <span>Execution</span>
                <span>→</span>
                <span>Review</span>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    setShowForm(false);
                    setError("");
                  }}
                  disabled={creating}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={creating}
                >
                  {creating
                    ? "Starting..."
                    : "Start Workflow"}
                </button>
              </div>
            </div>
          </form>
        </section>
      )}

      {/* ============================================
          WORKFLOW LIBRARY
      ============================================ */}
      <section className="dashboard-panel">
        <div className="panel-header">
          <div>
            <span className="panel-eyebrow">
              WORKFLOW LIBRARY
            </span>

            <h2>All Workflows</h2>

            <p>
              Workflow execution history from PostgreSQL.
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={loadWorkflows}
            disabled={loading}
          >
            {loading ? "Loading..." : "↻ Refresh"}
          </button>
        </div>

        {loading ? (
          <div className="empty-state">
            <div className="loading-spinner">
              ⟳
            </div>

            <strong>
              Loading workflows...
            </strong>

            <span>
              Fetching workflow history from PostgreSQL.
            </span>
          </div>
        ) : workflows.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              +
            </div>

            <strong>
              No workflows yet
            </strong>

            <span>
              Create your first workflow to start
              automating business operations.
            </span>

            <button
              type="button"
              className="primary-button"
              onClick={() => setShowForm(true)}
            >
              Create Your First Workflow
            </button>
          </div>
        ) : (
          <div className="workflow-list">
            {workflows.map((workflow) => {
              const status =
                String(
                  workflow.status || "UNKNOWN"
                ).toUpperCase();

              return (
                <Link
                  key={workflow.id}
                  to={`/workflows/${workflow.id}`}
                  className="workflow-card"
                >
                  <div className="workflow-card-icon">
                    WF
                  </div>

                  <div className="workflow-card-content">
                    <div className="workflow-card-title-row">
                      <h3>
                        {workflow.workflow_name}
                      </h3>

                      <span
                        className={getStatusClass(
                          workflow.status
                        )}
                      >
                        <span className="status-dot" />
                        {status}
                      </span>
                    </div>

                    <p className="workflow-request">
                      {workflow.input_data?.request ||
                        "No business request provided."}
                    </p>

                    <div className="workflow-meta">
                      <span>
                        Workflow #{workflow.id}
                      </span>

                      <span className="meta-divider">
                        •
                      </span>

                      <span>
                        State:{" "}
                        {getStateLabel(
                          workflow.current_state
                        )}
                      </span>

                      <span className="meta-divider">
                        •
                      </span>

                      <span>
                        Priority:{" "}
                        {getStateLabel(
                          workflow.input_data?.priority ||
                            "medium"
                        )}
                      </span>

                      <span className="meta-divider">
                        •
                      </span>

                      <span>
                        {workflow.created_at
                          ? new Date(
                              workflow.created_at
                            ).toLocaleString()
                          : "Unknown date"}
                      </span>
                    </div>
                  </div>

                  <div className="workflow-card-arrow">
                    →
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

export default Workflows;