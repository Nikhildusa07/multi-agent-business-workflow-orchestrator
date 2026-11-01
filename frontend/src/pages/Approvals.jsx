import { useEffect, useMemo, useState } from "react";
import {
  getApprovals,
  approveRequest,
  rejectRequest,
} from "../services/api";

function Approvals() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(null);
  const [filter, setFilter] = useState("ALL");

  const loadApprovals = async () => {
    try {
      setLoading(true);

      const response = await getApprovals();

      setApprovals(
        Array.isArray(response.data)
          ? response.data
          : []
      );
    } catch (error) {
      console.error(
        "Failed to load approvals:",
        error
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const statistics = useMemo(() => {
    const pending = approvals.filter(
      (approval) =>
        String(approval.status).toUpperCase() ===
        "PENDING"
    ).length;

    const approved = approvals.filter(
      (approval) =>
        String(approval.status).toUpperCase() ===
        "APPROVED"
    ).length;

    const rejected = approvals.filter(
      (approval) =>
        String(approval.status).toUpperCase() ===
        "REJECTED"
    ).length;

    return {
      total: approvals.length,
      pending,
      approved,
      rejected,
    };
  }, [approvals]);

  const filteredApprovals = useMemo(() => {
    if (filter === "ALL") {
      return approvals;
    }

    return approvals.filter(
      (approval) =>
        String(approval.status).toUpperCase() ===
        filter
    );
  }, [approvals, filter]);

  const handleApprove = async (id) => {
    setProcessing(id);

    try {
      await approveRequest(id, "admin");
      await loadApprovals();
    } catch (error) {
      console.error(
        "Approval failed:",
        error
      );

      alert("Approval failed.");
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (id) => {
    setProcessing(id);

    try {
      await rejectRequest(id, "admin");
      await loadApprovals();
    } catch (error) {
      console.error(
        "Rejection failed:",
        error
      );

      alert("Rejection failed.");
    } finally {
      setProcessing(null);
    }
  };

  const getStatusClass = (status) => {
    return `approval-status ${String(
      status || "UNKNOWN"
    ).toLowerCase()}`;
  };

  const formatDate = (date) => {
    if (!date) {
      return "Unknown date";
    }

    return new Date(date).toLocaleString();
  };

  return (
    <div className="page-container">
      {/* PAGE HEADER */}
      <div className="page-header">
        <div>
          <p className="eyebrow">
            HUMAN-IN-THE-LOOP
          </p>

          <h1>Approvals</h1>

          <p className="page-description">
            Review and authorize consequential
            workflow actions before execution.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={loadApprovals}
          disabled={loading}
        >
          {loading ? "Loading..." : "↻ Refresh"}
        </button>
      </div>

      {/* SUMMARY */}
      <div className="approval-summary-grid">
        <div className="approval-summary-card">
          <div className="summary-icon">A</div>

          <div>
            <span>Total Requests</span>
            <strong>{statistics.total}</strong>
          </div>
        </div>

        <div className="approval-summary-card pending-card">
          <div className="summary-icon">!</div>

          <div>
            <span>Pending</span>
            <strong>{statistics.pending}</strong>
          </div>
        </div>

        <div className="approval-summary-card approved-card">
          <div className="summary-icon">✓</div>

          <div>
            <span>Approved</span>
            <strong>{statistics.approved}</strong>
          </div>
        </div>

        <div className="approval-summary-card rejected-card">
          <div className="summary-icon">×</div>

          <div>
            <span>Rejected</span>
            <strong>{statistics.rejected}</strong>
          </div>
        </div>
      </div>

      {/* APPROVAL PANEL */}
      <section className="dashboard-panel">
        <div className="panel-header approval-panel-header">
          <div>
            <span className="panel-eyebrow">
              AUTHORIZATION QUEUE
            </span>

            <h2>Approval Requests</h2>

            <p>
              Human authorization history for
              consequential workflow actions.
            </p>
          </div>

          <div className="approval-filters">
            <button
              type="button"
              className={
                filter === "ALL"
                  ? "filter-button active"
                  : "filter-button"
              }
              onClick={() => setFilter("ALL")}
            >
              All
            </button>

            <button
              type="button"
              className={
                filter === "PENDING"
                  ? "filter-button active"
                  : "filter-button"
              }
              onClick={() =>
                setFilter("PENDING")
              }
            >
              Pending
            </button>

            <button
              type="button"
              className={
                filter === "APPROVED"
                  ? "filter-button active"
                  : "filter-button"
              }
              onClick={() =>
                setFilter("APPROVED")
              }
            >
              Approved
            </button>

            <button
              type="button"
              className={
                filter === "REJECTED"
                  ? "filter-button active"
                  : "filter-button"
              }
              onClick={() =>
                setFilter("REJECTED")
              }
            >
              Rejected
            </button>
          </div>
        </div>

        {loading ? (
          <div className="approval-empty-state">
            <div className="loading-spinner">
              ⟳
            </div>

            <strong>
              Loading approval requests...
            </strong>

            <span>
              Fetching authorization records from
              the backend.
            </span>
          </div>
        ) : filteredApprovals.length === 0 ? (
          <div className="approval-empty-state">
            <div className="empty-state-icon">
              ✓
            </div>

            <strong>
              No approval requests
            </strong>

            <span>
              There are no requests matching the
              selected filter.
            </span>
          </div>
        ) : (
          <div className="approval-list">
            {filteredApprovals.map((approval) => {
              const status = String(
                approval.status || "UNKNOWN"
              ).toUpperCase();

              const isPending =
                status === "PENDING";

              const isProcessing =
                processing === approval.id;

              return (
                <div
                  className={`approval-card ${
                    isPending
                      ? "approval-card-pending"
                      : ""
                  }`}
                  key={approval.id}
                >
                  {/* ICON */}
                  <div className="approval-card-icon">
                    {isPending ? "!" : "✓"}
                  </div>

                  {/* MAIN CONTENT */}
                  <div className="approval-card-content">
                    <div className="approval-card-top">
                      <div>
                        <span className="approval-id">
                          APPROVAL #{approval.id}
                        </span>

                        <h3>
                          Human Authorization Required
                        </h3>
                      </div>

                      <span
                        className={getStatusClass(
                          status
                        )}
                      >
                        <span className="status-dot" />
                        {status}
                      </span>
                    </div>

                    <p className="approval-description">
                      A consequential workflow action
                      requires human authorization before
                      it can continue.
                    </p>

                    <div className="approval-meta">
                      <div>
                        <span>
                          Workflow
                        </span>

                        <strong>
                          #{approval.workflow_id}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Task
                        </span>

                        <strong>
                          {approval.task_id
                            ? `#${approval.task_id}`
                            : "Workflow level"}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Requested By
                        </span>

                        <strong>
                          {approval.requested_by ||
                            "System"}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Created
                        </span>

                        <strong>
                          {formatDate(
                            approval.created_at
                          )}
                        </strong>
                      </div>
                    </div>

                    {approval.approved_by && (
                      <div className="approval-decision">
                        <span>
                          Decision by
                        </span>

                        <strong>
                          {approval.approved_by}
                        </strong>

                        {approval.approved_at && (
                          <span>
                            ·{" "}
                            {formatDate(
                              approval.approved_at
                            )}
                          </span>
                        )}
                      </div>
                    )}

                    {isPending && (
                      <div className="approval-actions">
                        <button
                          type="button"
                          className="primary-button"
                          disabled={isProcessing}
                          onClick={() =>
                            handleApprove(
                              approval.id
                            )
                          }
                        >
                          {isProcessing
                            ? "Processing..."
                            : "✓ Approve Request"}
                        </button>

                        <button
                          type="button"
                          className="secondary-button danger-button"
                          disabled={isProcessing}
                          onClick={() =>
                            handleReject(
                              approval.id
                            )
                          }
                        >
                          {isProcessing
                            ? "Processing..."
                            : "Reject"}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

export default Approvals;