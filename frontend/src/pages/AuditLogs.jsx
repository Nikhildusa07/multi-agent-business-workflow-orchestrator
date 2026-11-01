import { useEffect, useState } from "react";
import { getAuditLogs } from "../services/api";

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadLogs = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await getAuditLogs();

      console.log("AUDIT LOG API RESPONSE:", response.data);

      const data = Array.isArray(response.data)
        ? response.data
        : response.data?.logs || response.data?.items || [];

      setLogs(data);
    } catch (error) {
      console.error("Failed to load audit logs:", error);

      setLogs([]);

      if (error.response) {
        setError(
          `Backend error: ${error.response.status} ${
            error.response.statusText || ""
          }`
        );
      } else if (error.request) {
        setError("Unable to connect to backend.");
      } else {
        setError(error.message || "Failed to load audit logs.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <p className="eyebrow">OBSERVABILITY</p>

          <h1>Audit Logs</h1>

          <p className="page-description">
            Complete record of workflow and agent activity.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={loadLogs}
          disabled={loading}
        >
          ↻ Refresh
        </button>
      </div>

      <div className="panel audit-panel">
        <div className="panel-header">
          <div>
            <h2>Activity History</h2>

            <p>Agent actions and workflow events</p>
          </div>

          <span className="audit-count">
            {logs.length} {logs.length === 1 ? "event" : "events"}
          </span>
        </div>

        {loading ? (
          <div className="empty-state">
            Loading audit logs...
          </div>
        ) : error ? (
          <div className="empty-state">
            <strong>Failed to load audit logs</strong>
            <p>{error}</p>

            <button
              className="secondary-button"
              onClick={loadLogs}
            >
              ↻ Try Again
            </button>
          </div>
        ) : logs.length === 0 ? (
          <div className="empty-state">
            No audit logs found.
          </div>
        ) : (
          <div className="audit-list">
            {logs.map((log) => (
              <div
                className="audit-row"
                key={log.id}
              >
                <div className="audit-agent">
                  <strong>
                    {log.agent || "Unknown Agent"}
                  </strong>

                  <span>
                    Workflow #{log.workflow_id}
                    {log.task_id
                      ? ` · Task #${log.task_id}`
                      : ""}
                  </span>
                </div>

                <div className="audit-action">
                  <strong>
                    {log.action || "Unknown Action"}
                  </strong>
                </div>

                <div className="audit-status">
                  <span
                    className={`status-badge status-${String(
                      log.status || ""
                    ).toLowerCase()}`}
                  >
                    {log.status || "UNKNOWN"}
                  </span>
                </div>

                <div className="audit-message">
                  <p>
                    {log.message || "No message provided."}
                  </p>
                </div>

                <div className="audit-time">
                  <span>
                    {log.timestamp
                      ? new Date(
                          log.timestamp
                        ).toLocaleDateString()
                      : "-"}
                  </span>

                  <small>
                    {log.timestamp
                      ? new Date(
                          log.timestamp
                        ).toLocaleTimeString()
                      : "-"}
                  </small>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AuditLogs;