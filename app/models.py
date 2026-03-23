"""
Pydantic models for report requests, responses, and agent output bundles.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


class AgentOutputBundle(BaseModel):
    """Aggregated outputs from all specialist agents."""

    context_summary: Optional[dict] = Field(
        None, description="From Context Agent — dataset structure & quality info"
    )
    sql_results: Optional[list[dict]] = Field(
        None, description="From SQL Agent — query results"
    )
    charts: Optional[list[dict]] = Field(
        None,
        description="From Viz Agent — Plotly specs + PNG base64 images",
    )
    ml_results: Optional[dict] = Field(
        None, description="From ML Agent — model results & metrics"
    )
    nlp_insights: Optional[dict] = Field(
        None, description="From NLP Agent — text analysis results"
    )
    user_query: str = Field(
        ..., description="Original user query that triggered analysis"
    )
    analysis_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the analysis was performed",
    )


class BrandingConfig(BaseModel):
    """Branding customization for reports."""

    company_name: Optional[str] = None
    logo_base64: Optional[str] = None
    primary_color: str = "#1A56DB"


class ReportRequest(BaseModel):
    """Request model for report generation."""

    bundle: AgentOutputBundle
    report_style: Literal["executive", "technical", "detailed"] = "detailed"
    include_charts: bool = True
    export_format: Literal["json", "pdf", "docx", "pptx", "html"] = "json"
    branding: Optional[BrandingConfig] = None
    max_pages: int = Field(default=20, ge=1, le=100)


class SummaryRequest(BaseModel):
    """Request model for executive summary generation."""

    bundle: AgentOutputBundle
    max_words: int = Field(default=150, ge=50, le=500)


class NarrativeSections(BaseModel):
    """Generated narrative sections from LLM."""

    data_overview: Optional[str] = None
    sql_findings: Optional[str] = None
    ml_insights: Optional[str] = None
    nlp_section: Optional[str] = None
    executive_summary: Optional[str] = None


class ReportMetadata(BaseModel):
    """Metadata stored in cache for generated reports."""

    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    format: str
    style: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    content_base64: Optional[str] = None
    user_query: str = ""
    sections_generated: list[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    """Response model for report generation."""

    report_id: str
    format: str
    style: str
    created_at: datetime
    download_url: Optional[str] = None
    content_base64: Optional[str] = None
    narratives: Optional[NarrativeSections] = None
    metadata: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    service: str = "report-synthesis-agent"
    version: str = "1.0.0"
    llm_provider: str = ""
    storage_type: str = ""
