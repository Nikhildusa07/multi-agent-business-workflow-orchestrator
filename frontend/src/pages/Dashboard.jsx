import React from "react";
import { Link } from "react-router-dom";

const stats = [
  { label: "Total Workflows", value: "12", icon: "↗" },
  { label: "Running", value: "03", icon: "◉" },
  { label: "Completed", value: "08", icon: "✓" },
  { label: "Failed", value: "01", icon: "!" },
];

const workflows = [
  {
    name: "Business Performance Report",
    category: "Business Analysis",
    priority: "High",
    status: "COMPLETED",
    tasks: "3 / 3",
    time: "2 min ago",
  },
  {
    name: "Customer Support Response",
    category: "Customer Support",
    priority: "Medium",
    status: "RUNNING",
    tasks: "2 / 3",
    time: "5 min ago",
  },
  {
    name: "Monthly Sales Analysis",
    category: "Business Analysis",
    priority: "High",
    status: "COMPLETED",
    tasks: "4 / 4",
    time: "18 min ago",
  },
  {
    name: "Client Communication",
    category: "Communication",
    priority: "Low",
    status: "FAILED",
    tasks: "1 / 2",
    time: "32 min ago",
  },
];

const agents = [
  {
    name: "Intake Agent",
    description: "Request classification",
    status: "ACTIVE",
  },
  {
    name: "Planning Agent",
    description: "Task planning",
    status: "ACTIVE",
  },
  {
    name: "Execution Agent",
    description: "Task execution",
    status: "ACTIVE",
  },
  {
    name: "Review Agent",
    description: "Quality validation",
    status: "ACTIVE",
  },
];

function Dashboard() {
  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <p className="eyebrow">AI OPERATIONS CENTER</p>
          <h1>Workflow Dashboard</h1>
          <p className="page-description">
            Monitor and control your multi-agent business workflows.
          </p>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          All Systems Operational
        </div>
      </div>

      <section className="stats-grid">
        {stats.map((stat) => (
          <div className="stat-card" key={stat.label}>
            <div className="stat-top">
              <span className="stat-label">{stat.label}</span>
              <span className="stat-icon">{stat.icon}</span>
            </div>

            <div className="stat-value">{stat.value}</div>

            <div className="stat-footer">
              <span>Current status</span>
            </div>
          </div>
        ))}
      </section>

      <section className="dashboard-grid">
        <div className="panel workflows-panel">
          <div className="panel-header">
            <div>
              <h2>Recent Workflows</h2>
              <p>Latest workflow executions</p>
            </div>

            <Link to="/workflows" className="secondary-button">
              View All
            </Link>
          </div>

          <div className="workflow-list">
            {workflows.map((workflow) => (
              <div className="workflow-row" key={workflow.name}>
                <div className="workflow-main">
                  <div className="workflow-avatar">
                    {workflow.name.charAt(0)}
                  </div>

                  <div>
                    <h3>{workflow.name}</h3>
                    <p>
                      {workflow.category} · {workflow.tasks} tasks
                    </p>
                  </div>
                </div>

                <div className="workflow-meta">
                  <span
                    className={`priority priority-${workflow.priority.toLowerCase()}`}
                  >
                    {workflow.priority}
                  </span>

                  <span
                    className={`status-badge status-${workflow.status.toLowerCase()}`}
                  >
                    {workflow.status}
                  </span>

                  <span className="workflow-time">
                    {workflow.time}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel agents-panel">
          <div className="panel-header">
            <div>
              <h2>Agent Activity</h2>
              <p>Current orchestration pipeline</p>
            </div>
          </div>

          <div className="agent-list">
            {agents.map((agent, index) => (
              <div className="agent-item" key={agent.name}>
                <div className="agent-number">{index + 1}</div>

                <div className="agent-info">
                  <h3>{agent.name}</h3>
                  <p>{agent.description}</p>
                </div>

                <span className="agent-status">
                  <span className="mini-dot"></span>
                  {agent.status}
                </span>
              </div>
            ))}
          </div>

          <div className="pipeline">
            <div className="pipeline-line"></div>

            <div className="pipeline-step active">
              <span>1</span>
              <small>Intake</small>
            </div>

            <div className="pipeline-step active">
              <span>2</span>
              <small>Plan</small>
            </div>

            <div className="pipeline-step active">
              <span>3</span>
              <small>Execute</small>
            </div>

            <div className="pipeline-step active">
              <span>4</span>
              <small>Review</small>
            </div>
          </div>
        </div>
      </section>

      <section className="bottom-grid">
        <div className="panel health-panel">
          <div className="panel-header">
            <div>
              <h2>System Health</h2>
              <p>Infrastructure status</p>
            </div>
          </div>

          <div className="health-list">
            <div className="health-item">
              <span>FastAPI</span>
              <strong>Healthy</strong>
              <span className="health-dot"></span>
            </div>

            <div className="health-item">
              <span>PostgreSQL</span>
              <strong>Connected</strong>
              <span className="health-dot"></span>
            </div>

            <div className="health-item">
              <span>Redis</span>
              <strong>Connected</strong>
              <span className="health-dot"></span>
            </div>

            <div className="health-item">
              <span>OpenTelemetry</span>
              <strong>Active</strong>
              <span className="health-dot"></span>
            </div>
          </div>
        </div>

        <div className="panel approval-panel">
          <div className="panel-header">
            <div>
              <h2>Human Approval</h2>
              <p>Consequential actions requiring review</p>
            </div>

            <span className="approval-count">01</span>
          </div>

          <div className="approval-card">
            <div className="approval-icon">!</div>

            <div>
              <h3>Pending Approval</h3>
              <p>
                One workflow action requires human authorization.
              </p>
            </div>

            <Link to="/approvals" className="primary-button">
              Review
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;