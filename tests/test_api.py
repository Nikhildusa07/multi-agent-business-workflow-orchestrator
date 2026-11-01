from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] in ["healthy", "degraded"]
    assert "postgresql" in data["services"]
    assert "redis" in data["services"]


def test_create_workflow():
    payload = {
        "workflow_name": "Pytest Business Workflow",
        "input_data": {
            "request": "Create a business performance report",
            "priority": "medium",
        },
    }

    response = client.post("/workflows/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["workflow_name"] == "Pytest Business Workflow"
    assert data["status"] == "PENDING"
    assert data["current_state"] == "PENDING"
    assert data["id"] is not None


def test_get_workflows():
    response = client.get("/workflows/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_workflow_execution():
    create_payload = {
        "workflow_name": "Pytest Execution Workflow",
        "input_data": {
            "request": "Create a business performance report",
            "priority": "medium",
        },
    }

    create_response = client.post(
        "/workflows/",
        json=create_payload,
    )

    assert create_response.status_code == 201

    workflow_id = create_response.json()["id"]

    run_response = client.post(
        f"/workflows/{workflow_id}/run"
    )

    assert run_response.status_code == 200

    data = run_response.json()

    assert data["id"] == workflow_id
    assert data["status"] == "COMPLETED"
    assert data["error_message"] is None


def test_get_workflow():
    create_payload = {
        "workflow_name": "Pytest Get Workflow",
        "input_data": {
            "request": "Analyze business performance",
            "priority": "low",
        },
    }

    create_response = client.post(
        "/workflows/",
        json=create_payload,
    )

    assert create_response.status_code == 201

    workflow_id = create_response.json()["id"]

    response = client.get(
        f"/workflows/{workflow_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == workflow_id
    assert data["workflow_name"] == "Pytest Get Workflow"


def test_get_approvals():
    response = client.get("/approvals/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_audit_logs():
    response = client.get("/audit-logs/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)