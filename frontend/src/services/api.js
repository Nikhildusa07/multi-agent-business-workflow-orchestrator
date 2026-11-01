import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// ================================
// Workflows
// ================================

export const getWorkflows = () =>
  api.get("/workflows/");

export const getWorkflow = (id) =>
  api.get(`/workflows/${id}`);

export const createWorkflow = (data) =>
  api.post("/workflows/", data);

export const runWorkflow = (id) =>
  api.post(`/workflows/${id}/run`);

// ================================
// Approvals
// ================================

export const getApprovals = () =>
  api.get("/approvals/");

export const approveRequest = (id, approvedBy) =>
  api.post(`/approvals/${id}/approve`, {
    approved_by: approvedBy,
  });

export const rejectRequest = (id, rejectedBy) =>
  api.post(`/approvals/${id}/reject`, {
    approved_by: rejectedBy,
  });

// ================================
// Audit Logs
// ================================

export const getAuditLogs = () =>
  api.get("/audit-logs/");

// ================================
// System Health
// ================================

export const getSystemHealth = () =>
  api.get("/health");

export default api;