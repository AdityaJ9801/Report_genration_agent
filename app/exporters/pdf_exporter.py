"""
WeasyPrint-based PDF exporter.
Renders Jinja2 HTML template → PDF with embedded chart images and branding.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from app.config import settings
from app.models import NarrativeSections, BrandingConfig

logger = logging.getLogger(__name__)


def _get_template_env() -> Environment:
    """Create Jinja2 environment pointing at template directory."""
    template_dir = Path(settings.TEMPLATE_DIR)
    if not template_dir.exists():
        # Fallback for Docker vs local dev
        template_dir = Path(__file__).parent.parent / "templates"
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )


def export_pdf(
    narratives: NarrativeSections,
    charts: Optional[list[dict]] = None,
    branding: Optional[BrandingConfig] = None,
    report_style: str = "detailed",
    user_query: str = "",
    include_charts: bool = True,
) -> bytes:
    """
    Generate a PDF report from narrative sections.

    Args:
        narratives: Generated narrative text sections
        charts: List of chart dicts with 'image_base64' and 'title' keys
        branding: Optional branding configuration
        report_style: 'executive', 'technical', or 'detailed'
        user_query: Original user query
        include_charts: Whether to include chart images

    Returns:
        PDF file as bytes
    """
    from weasyprint import HTML, CSS

    env = _get_template_env()
    template = env.get_template("base_report.html.j2")

    # Prepare chart data for template
    chart_data = []
    if include_charts and charts:
        for chart in charts:
            chart_data.append(
                {
                    "title": chart.get("title", "Chart"),
                    "image_base64": chart.get("image_base64", chart.get("png_base64", "")),
                    "description": chart.get("description", ""),
                }
            )

    # Prepare branding defaults
    brand = branding or BrandingConfig()

    # Render HTML
    html_content = template.render(
        narratives=narratives,
        charts=chart_data,
        branding=brand,
        report_style=report_style,
        user_query=user_query,
        include_charts=include_charts and bool(chart_data),
    )

    # Load CSS
    css_path = Path(settings.STATIC_DIR) / "styles" / "report.css"
    if not css_path.exists():
        css_path = Path(__file__).parent.parent.parent / "static" / "styles" / "report.css"

    stylesheets = []
    if css_path.exists():
        stylesheets.append(CSS(filename=str(css_path)))

    # Generate PDF
    pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=stylesheets)
    logger.info(f"Generated PDF report ({len(pdf_bytes)} bytes)")
    return pdf_bytes
