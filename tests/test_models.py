"""
Tests for Pydantic models: AgentOutputBundle, ReportRequest, etc.
"""

import pytest
from datetime import datetime

from app.models import (
    AgentOutputBundle,
    ReportRequest,
    SummaryRequest,
    NarrativeSections,
    ReportMetadata,
    BrandingConfig,
    HealthResponse,
)


class TestAgentOutputBundle:
    """Test AgentOutputBundle model validation."""

    def test_full_bundle(self, full_bundle):
        """All fields populated."""
        assert full_bundle.context_summary is not None
        assert len(full_bundle.sql_results) == 4
        assert len(full_bundle.charts) == 2
        assert full_bundle.ml_results is not None
        assert full_bundle.nlp_insights is not None
        assert full_bundle.user_query != ""

    def test_minimal_bundle(self, minimal_bundle):
        """Only required field (user_query)."""
        assert minimal_bundle.user_query == "Simple analysis request"
        assert minimal_bundle.context_summary is None
        assert minimal_bundle.sql_results is None
        assert minimal_bundle.charts is None
        assert minimal_bundle.ml_results is None
        assert minimal_bundle.nlp_insights is None

    def test_partial_bundle(self, partial_bundle):
        """Some optional fields populated."""
        assert partial_bundle.context_summary is not None
        assert partial_bundle.sql_results is not None
        assert partial_bundle.ml_results is None
        assert partial_bundle.nlp_insights is None

    def test_missing_user_query_raises(self):
        """user_query is required."""
        with pytest.raises(Exception):
            AgentOutputBundle()

    def test_default_timestamp(self):
        """analysis_timestamp defaults to current time."""
        bundle = AgentOutputBundle(user_query="test")
        assert isinstance(bundle.analysis_timestamp, datetime)


class TestReportRequest:
    """Test ReportRequest model validation."""

    def test_defaults(self, minimal_bundle):
        req = ReportRequest(bundle=minimal_bundle)
        assert req.report_style == "detailed"
        assert req.include_charts is True
        assert req.export_format == "json"
        assert req.branding is None
        assert req.max_pages == 20

    def test_custom_values(self, full_bundle, sample_branding):
        req = ReportRequest(
            bundle=full_bundle,
            report_style="executive",
            include_charts=False,
            export_format="pdf",
            branding=sample_branding,
            max_pages=10,
        )
        assert req.report_style == "executive"
        assert req.export_format == "pdf"
        assert req.branding.company_name == "Acme Analytics Corp"
        assert req.max_pages == 10

    def test_invalid_format(self, minimal_bundle):
        with pytest.raises(Exception):
            ReportRequest(bundle=minimal_bundle, export_format="xlsx")

    def test_invalid_style(self, minimal_bundle):
        with pytest.raises(Exception):
            ReportRequest(bundle=minimal_bundle, report_style="fancy")

    def test_max_pages_bounds(self, minimal_bundle):
        with pytest.raises(Exception):
            ReportRequest(bundle=minimal_bundle, max_pages=0)
        with pytest.raises(Exception):
            ReportRequest(bundle=minimal_bundle, max_pages=200)


class TestNarrativeSections:
    """Test NarrativeSections model."""

    def test_all_none(self):
        ns = NarrativeSections()
        assert ns.data_overview is None
        assert ns.executive_summary is None

    def test_partial(self):
        ns = NarrativeSections(
            data_overview="Test overview",
            executive_summary="Test summary",
        )
        assert ns.data_overview == "Test overview"
        assert ns.sql_findings is None


class TestReportMetadata:
    """Test ReportMetadata model."""

    def test_defaults(self):
        meta = ReportMetadata(format="pdf", style="detailed")
        assert meta.report_id is not None
        assert len(meta.report_id) == 36  # UUID
        assert isinstance(meta.created_at, datetime)
        assert meta.sections_generated == []

    def test_with_sections(self):
        meta = ReportMetadata(
            format="docx",
            style="executive",
            sections_generated=["data_overview", "executive_summary"],
        )
        assert len(meta.sections_generated) == 2


class TestBrandingConfig:
    """Test BrandingConfig model."""

    def test_defaults(self):
        brand = BrandingConfig()
        assert brand.primary_color == "#1A56DB"
        assert brand.company_name is None
        assert brand.logo_base64 is None

    def test_custom(self, sample_branding):
        assert sample_branding.company_name == "Acme Analytics Corp"
        assert sample_branding.primary_color == "#2563EB"


class TestHealthResponse:
    """Test HealthResponse model."""

    def test_defaults(self):
        health = HealthResponse()
        assert health.status == "healthy"
        assert health.service == "report-synthesis-agent"
        assert health.version == "1.0.0"
