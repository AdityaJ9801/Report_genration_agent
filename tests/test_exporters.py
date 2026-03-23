"""
Tests for export engines (DOCX, PPTX).
PDF tests are skipped on Windows if WeasyPrint system libraries are not available.
"""

import io
import pytest
import sys

from app.models import NarrativeSections, BrandingConfig


class TestDocxExporter:
    """Test DOCX file generation."""

    def test_full_docx(self, sample_narratives, sample_charts, sample_branding, sample_sql_results):
        from app.exporters.docx_exporter import export_docx

        result = export_docx(
            narratives=sample_narratives,
            charts=sample_charts,
            branding=sample_branding,
            report_style="detailed",
            user_query="Test query",
            include_charts=True,
            sql_results=sample_sql_results,
        )
        assert isinstance(result, bytes)
        assert len(result) > 0
        # DOCX magic bytes (PK zip)
        assert result[:2] == b"PK"

    def test_minimal_docx(self):
        from app.exporters.docx_exporter import export_docx

        narratives = NarrativeSections(
            executive_summary="Brief summary of findings."
        )
        result = export_docx(
            narratives=narratives,
            report_style="executive",
            user_query="Minimal test",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result[:2] == b"PK"

    def test_no_charts_docx(self, sample_narratives):
        from app.exporters.docx_exporter import export_docx

        result = export_docx(
            narratives=sample_narratives,
            include_charts=False,
            user_query="No charts test",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_docx_with_branding(self, sample_narratives, sample_branding):
        from app.exporters.docx_exporter import export_docx

        result = export_docx(
            narratives=sample_narratives,
            branding=sample_branding,
            user_query="Branding test",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_docx_with_sql_table(self, sample_narratives, sample_sql_results):
        from app.exporters.docx_exporter import export_docx

        result = export_docx(
            narratives=sample_narratives,
            sql_results=sample_sql_results,
            user_query="SQL table test",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestPptxExporter:
    """Test PPTX file generation."""

    def test_full_pptx(self, sample_narratives, sample_charts, sample_branding):
        from app.exporters.pptx_exporter import export_pptx

        result = export_pptx(
            narratives=sample_narratives,
            charts=sample_charts,
            branding=sample_branding,
            report_style="detailed",
            user_query="Test query",
            include_charts=True,
        )
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PPTX magic bytes (PK zip)
        assert result[:2] == b"PK"

    def test_minimal_pptx(self):
        from app.exporters.pptx_exporter import export_pptx

        narratives = NarrativeSections(
            executive_summary="Brief summary for slides."
        )
        result = export_pptx(
            narratives=narratives,
            report_style="executive",
            user_query="Minimal presentation",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pptx_no_charts(self, sample_narratives):
        from app.exporters.pptx_exporter import export_pptx

        result = export_pptx(
            narratives=sample_narratives,
            include_charts=False,
            user_query="No charts test",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pptx_with_branding(self, sample_narratives, sample_branding):
        from app.exporters.pptx_exporter import export_pptx

        result = export_pptx(
            narratives=sample_narratives,
            branding=sample_branding,
            user_query="Branding test",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pptx_slide_count(self, sample_narratives):
        """Verify correct number of slides."""
        from pptx import Presentation as PptxPresentation
        from app.exporters.pptx_exporter import export_pptx

        result = export_pptx(
            narratives=sample_narratives,
            user_query="Slide count test",
        )
        prs = PptxPresentation(io.BytesIO(result))
        # Title + Exec Summary + 4 sections + Key Takeaways = 7 slides
        assert len(prs.slides) == 7


class TestPdfExporter:
    """Test PDF generation (skipped on Windows without WeasyPrint system libs)."""

    @pytest.fixture(autouse=True)
    def _check_weasyprint(self):
        """Skip PDF tests if WeasyPrint is not available."""
        try:
            import weasyprint
            weasyprint.HTML(string="<p>test</p>").write_pdf()
        except Exception:
            pytest.skip("WeasyPrint system libraries not available")

    def test_full_pdf(self, sample_narratives, sample_charts, sample_branding):
        from app.exporters.pdf_exporter import export_pdf

        result = export_pdf(
            narratives=sample_narratives,
            charts=sample_charts,
            branding=sample_branding,
            report_style="detailed",
            user_query="Test query",
            include_charts=True,
        )
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PDF magic bytes
        assert result[:4] == b"%PDF"

    def test_minimal_pdf(self):
        from app.exporters.pdf_exporter import export_pdf

        narratives = NarrativeSections(
            executive_summary="Brief PDF summary."
        )
        result = export_pdf(
            narratives=narratives,
            report_style="executive",
            user_query="Minimal PDF",
        )
        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"
