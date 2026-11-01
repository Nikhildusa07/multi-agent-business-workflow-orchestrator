import React from "react";
import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Workflows from "./pages/Workflows";
import Approvals from "./pages/Approvals";
import AuditLogs from "./pages/AuditLogs";
import SystemHealth from "./pages/SystemHealth";
import WorkflowDetails from "./pages/WorkflowDetails";

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <aside className="sidebar">
          <div className="brand">
            <div className="brand-mark">W</div>

            <div>
              <h2>WorkflowOS</h2>
              <span>AI Orchestrator</span>
            </div>
          </div>

          <nav className="navigation">
            <p className="nav-section">MAIN</p>

            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              <span>▦</span>
              Dashboard
            </NavLink>

            <NavLink
              to="/workflows"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              <span>◈</span>
              Workflows
            </NavLink>

            <NavLink
              to="/approvals"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              <span>✓</span>
              Approvals
            </NavLink>

            <p className="nav-section nav-section-spaced">
              MONITORING
            </p>

            <NavLink
              to="/audit-logs"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              <span>≡</span>
              Audit Logs
            </NavLink>

            <NavLink
              to="/system"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              <span>◉</span>
              System Health
            </NavLink>
          </nav>

          <div className="sidebar-bottom">
            <div className="environment">
              <span className="environment-dot"></span>

              <div>
                <strong>Development</strong>
                <small>Local environment</small>
              </div>
            </div>

            <div className="user-card">
              <div className="user-avatar">N</div>

              <div>
                <strong>Admin</strong>
                <small>Workflow Manager</small>
              </div>
            </div>
          </div>
        </aside>

        <main className="main-content">
          <header className="topbar">
            <div className="breadcrumb">
              <span>WorkflowOS</span>
              <span>/</span>
              <strong>AI Orchestrator</strong>
            </div>

            <div className="topbar-actions">
              <span className="api-indicator">
                <span></span>
                API Connected
              </span>

              <button className="icon-button">⌕</button>
              <button className="icon-button">⚙</button>
            </div>
          </header>

          <Routes>
            <Route path="/" element={<Dashboard />} />

            <Route
              path="/workflows"
              element={<Workflows />}
            />

            <Route
              path="/workflows/:workflowId"
              element={<WorkflowDetails />}
            />

            <Route
              path="/approvals"
              element={<Approvals />}
            />

            <Route
              path="/audit-logs"
              element={<AuditLogs />}
            />

            <Route
              path="/system"
              element={<SystemHealth />}
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;