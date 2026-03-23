"""
Tests for FastAPI endpoints with mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from fastapi.testclient import TestClient

from app.models import NarrativeSections, ReportMetadata


# Mock external dependencies before importing app
@pytest.fixture
def client():
    """Create a test client with mocked narrative generator and cache."""
    mock_narratives = NarrativeSections(
        data_overview="Test data overview narrative.",
        sql_findings="Test SQL findings narrative.",
        ml_insights="Test ML insights narrative.",
        nlp_section="Test NLP section narrative.",
        executive_summary="Test executive summary narrative.",
    )

    with patch("app.main.generate_all_narratives", new_callable=AsyncMock) as mock_gen, \
         patch("app.main.write_executive_summary", new_callable=AsyncMock) as mock_exec, \
         patch("app.main.store_report_metadata", new_callable=AsyncMock) as mock_store, \
         patch("app.main.get_report_metadata", new_callable=AsyncMock) as mock_get:

        mock_gen.return_value = mock_narratives
        mock_exec.return_value = "Mock executive summary."
        mock_store.return_value = True
        mock_get.return_value = None  # Default: cache miss

        from app.main import app
        yield TestClient(app), mock_gen, mock_exec, mock_store, mock_get


class TestHealthEndpoint:
    """Test the /health endpoint."""

    def test_health_returns_200(self, client):
        test_client, *_ = client
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "report-synthesis-agent"
        assert data["version"] == "1.0.0"


class TestReportEndpoint:
    """Test the /report endpoint."""

    def _make_request_body(self, export_format="json"):
        return {
            "bundle": {
                "context_summary": {"dataset": "test", "rows": 100},
                "sql_results": [{"col1": "val1", "col2": 42}],
                "user_query": "Test analysis query",
            },
            "report_style": "detailed",
            "export_format": export_format,
        }

    def test_report_json_format(self, client):
        test_client, mock_gen, *_ = client
        response = test_client.post("/report", json=self._make_request_body("json"))
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "json"
        assert data["report_id"] is not None
        assert data["narratives"]["data_overview"] is not None
        assert data["narratives"]["executive_summary"] is not None

    def test_report_docx_format(self, client):
        test_client, mock_gen, *_ = client

        # Mock the DOCX exporter to avoid actual file generation
        with patch("app.main._export_report", new_callable=AsyncMock) as mock_export:
            mock_export.return_value = ReportMetadata(
                format="docx",
                style="detailed",
                user_query="Test",
                content_base64="dGVzdA==",
                sections_generated=["data_overview"],
            )
            response = test_client.post("/report", json=self._make_request_body("docx"))
            assert response.status_code == 200
            data = response.json()
            assert data["format"] == "docx"

    def test_report_invalid_body(self, client):
        test_client, *_ = client
        response = test_client.post("/report", json={"invalid": "body"})
        assert response.status_code == 422  # Validation error


class TestSummaryEndpoint:
    """Test the /summary endpoint."""

    def test_summary_generation(self, client):
        test_client, _, mock_exec, *_ = client
        body = {
            "bundle": {
                "context_summary": {"dataset": "test"},
                "user_query": "Summarize this",
            },
            "max_words": 150,
        }
        response = test_client.post("/summary", json=body)
        assert response.status_code == 200
        data = response.json()
        assert data["style"] == "executive"
        assert data["format"] == "json"


class TestCachedReportEndpoint:
    """Test the /report/{id} endpoint."""

    def test_report_not_found(self, client):
        test_client, *_, mock_get = client
        mock_get.return_value = None
        response = test_client.get("/report/nonexistent-id")
        assert response.status_code == 404

    def test_report_found(self, client):
        test_client, *_, mock_get = client
        mock_get.return_value = ReportMetadata(
            report_id="test-id-123",
            format="json",
            style="detailed",
            user_query="Test query",
            sections_generated=["data_overview", "executive_summary"],
        )
        response = test_client.get("/report/test-id-123")
        assert response.status_code == 200
        data = response.json()
        assert data["report_id"] == "test-id-123"
        assert data["format"] == "json"


class TestExportEndpoints:
    """Test the /export/* endpoints."""

    def test_export_pdf_endpoint(self, client):
        test_client, *_ = client
        with patch("app.main._export_report", new_callable=AsyncMock) as mock_export:
            mock_export.return_value = ReportMetadata(
                format="pdf", style="detailed", user_query="Test",
                content_base64="dGVzdA==", sections_generated=["data_overview"],
            )
            body = {
                "bundle": {
                    "user_query": "PDF test",
                    "context_summary": {"test": True},
                },
            }
            response = test_client.post("/export/pdf", json=body)
            assert response.status_code == 200

    def test_export_docx_endpoint(self, client):
        test_client, *_ = client
        with patch("app.main._export_report", new_callable=AsyncMock) as mock_export:
            mock_export.return_value = ReportMetadata(
                format="docx", style="detailed", user_query="Test",
                content_base64="dGVzdA==", sections_generated=["data_overview"],
            )
            body = {
                "bundle": {
                    "user_query": "DOCX test",
                    "context_summary": {"test": True},
                },
            }
            response = test_client.post("/export/docx", json=body)
            assert response.status_code == 200

    def test_export_pptx_endpoint(self, client):
        test_client, *_ = client
        with patch("app.main._export_report", new_callable=AsyncMock) as mock_export:
            mock_export.return_value = ReportMetadata(
                format="pptx", style="detailed", user_query="Test",
                content_base64="dGVzdA==", sections_generated=["data_overview"],
            )
            body = {
                "bundle": {
                    "user_query": "PPTX test",
                    "context_summary": {"test": True},
                },
            }
            response = test_client.post("/export/pptx", json=body)
            assert response.status_code == 200
