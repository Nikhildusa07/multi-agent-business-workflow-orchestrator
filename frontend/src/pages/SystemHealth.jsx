import { useEffect, useState } from "react";
import { getSystemHealth } from "../services/api";

function SystemHealth() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const loadHealth = async () => {
    try {
      setLoading(true);
      setError(false);

      const response = await getSystemHealth();
      setHealth(response.data);
    } catch (err) {
      console.error("Failed to load system health:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHealth();
  }, []);

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <p className="eyebrow">WORKFLOW ORCHESTRATOR</p>
            <h1>System Health</h1>
            <p className="page-description">
              Monitor the health of the orchestration infrastructure.
            </p>
          </div>
        </div>

        <div className="panel">
          <div className="empty-state">
            Checking system health...
          </div>
        </div>
      </div>
    );
  }

  if (error || !health) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <p className="eyebrow">WORKFLOW ORCHESTRATOR</p>
            <h1>System Health</h1>
            <p className="page-description">
              Monitor the health of the orchestration infrastructure.
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            System Unavailable
          </div>
        </div>

        <div className="panel">
          <div className="empty-state">
            Unable to connect to the health service.
          </div>
        </div>
      </div>
    );
  }

  const overallStatus = health.status || "unknown";
  const environment = health.environment || "unknown";

  const postgresStatus =
    health.services?.postgresql?.status || "unknown";

  const redisStatus =
    health.services?.redis?.status || "unknown";

  const isOverallHealthy = overallStatus === "healthy";

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <p className="eyebrow">WORKFLOW ORCHESTRATOR</p>

          <h1>System Health</h1>

          <p className="page-description">
            Monitor the health of the orchestration infrastructure.
          </p>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>

          {isOverallHealthy
            ? "All Systems Operational"
            : "System Degraded"}
        </div>
      </div>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">
              Overall Status
            </span>

            <span className="stat-icon">✓</span>
          </div>

          <div className="stat-value">
            {overallStatus.toUpperCase()}
          </div>

          <div className="stat-footer">
            <span>System status</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">
              PostgreSQL
            </span>

            <span className="stat-icon">◉</span>
          </div>

          <div className="stat-value">
            {postgresStatus.toUpperCase()}
          </div>

          <div className="stat-footer">
            <span>Database service</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">
              Redis
            </span>

            <span className="stat-icon">◉</span>
          </div>

          <div className="stat-value">
            {redisStatus.toUpperCase()}
          </div>

          <div className="stat-footer">
            <span>Cache service</span>
          </div>
        </div>
      </section>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Infrastructure Services</h2>

            <p>
              Live backend service health
            </p>
          </div>
        </div>

        <div className="health-list">
          <div className="health-item">
            <span>FastAPI</span>

            <strong>
              {overallStatus === "healthy"
                ? "Healthy"
                : "Unavailable"}
            </strong>

            <span className="health-dot"></span>
          </div>

          <div className="health-item">
            <span>PostgreSQL</span>

            <strong>
              {postgresStatus === "healthy"
                ? "Connected"
                : "Unavailable"}
            </strong>

            <span className="health-dot"></span>
          </div>

          <div className="health-item">
            <span>Redis</span>

            <strong>
              {redisStatus === "healthy"
                ? "Connected"
                : "Unavailable"}
            </strong>

            <span className="health-dot"></span>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Environment</h2>

            <p>
              Current application configuration
            </p>
          </div>
        </div>

        <div className="health-list">
          <div className="health-item">
            <span>Environment</span>

            <strong>
              {environment}
            </strong>
          </div>

          <div className="health-item">
            <span>Overall Status</span>

            <strong>
              {overallStatus}
            </strong>
          </div>
        </div>
      </div>

      <div className="page-actions">
        <button
          className="secondary-button"
          onClick={loadHealth}
        >
          ↻ Refresh
        </button>
      </div>
    </div>
  );
}

export default SystemHealth;