"""
Tests for narrative generation with mocked LLM responses.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.narrative import (
    write_data_overview,
    write_sql_findings,
    write_ml_insights,
    write_nlp_section,
    write_executive_summary,
    generate_all_narratives,
    _build_data_overview_prompt,
    _build_sql_findings_prompt,
    _build_ml_insights_prompt,
    _build_nlp_section_prompt,
    _build_executive_summary_prompt,
)


class TestPromptBuilders:
    """Test that prompt builders produce correct prompts."""

    def test_data_overview_prompt(self, sample_context_summary):
        prompt = _build_data_overview_prompt(sample_context_summary)
        assert "dataset" in prompt.lower()
        assert "sales_data_2024" in prompt

    def test_sql_findings_prompt(self, sample_sql_results):
        prompt = _build_sql_findings_prompt(sample_sql_results)
        assert "SQL" in prompt or "query" in prompt.lower()
        assert "North" in prompt

    def test_ml_insights_prompt(self, sample_ml_results):
        prompt = _build_ml_insights_prompt(sample_ml_results)
        assert "machine learning" in prompt.lower() or "ML" in prompt
        assert "Random Forest" in prompt

    def test_nlp_section_prompt(self, sample_nlp_insights):
        prompt = _build_nlp_section_prompt(sample_nlp_insights)
        assert "NLP" in prompt or "sentiment" in prompt.lower()

    def test_executive_summary_prompt(self):
        sections = {
            "data_overview": "Some data overview text",
            "sql_findings": "Some SQL findings text",
        }
        prompt = _build_executive_summary_prompt(sections)
        assert "executive summary" in prompt.lower()
        assert "Some data overview text" in prompt

    def test_executive_summary_skips_empty_sections(self):
        sections = {
            "data_overview": "Overview text",
            "sql_findings": None,
            "ml_insights": "",
        }
        prompt = _build_executive_summary_prompt(sections)
        assert "Overview text" in prompt
        # None/empty sections should not appear
        assert "None" not in prompt


class TestSectionWriters:
    """Test individual section writers with mocked LLM."""

    @pytest.mark.asyncio
    async def test_write_data_overview(self, sample_context_summary, mock_llm_client):
        result = await write_data_overview(sample_context_summary)
        assert result is not None
        mock_llm_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_data_overview_none(self, mock_llm_client):
        result = await write_data_overview(None)
        assert result is None
        mock_llm_client.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_write_sql_findings(self, sample_sql_results, mock_llm_client):
        result = await write_sql_findings(sample_sql_results)
        assert result is not None
        mock_llm_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_sql_findings_none(self, mock_llm_client):
        result = await write_sql_findings(None)
        assert result is None
        mock_llm_client.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_write_sql_findings_empty_list(self, mock_llm_client):
        result = await write_sql_findings([])
        assert result is None
        mock_llm_client.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_write_ml_insights(self, sample_ml_results, mock_llm_client):
        result = await write_ml_insights(sample_ml_results)
        assert result is not None
        mock_llm_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_ml_insights_none(self, mock_llm_client):
        result = await write_ml_insights(None)
        assert result is None
        mock_llm_client.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_write_nlp_section(self, sample_nlp_insights, mock_llm_client):
        result = await write_nlp_section(sample_nlp_insights)
        assert result is not None
        mock_llm_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_nlp_section_none(self, mock_llm_client):
        result = await write_nlp_section(None)
        assert result is None
        mock_llm_client.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_write_executive_summary(self, mock_llm_client):
        sections = {"data_overview": "Some text", "sql_findings": "More text"}
        result = await write_executive_summary(sections)
        assert result is not None
        mock_llm_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_executive_summary_all_empty(self, mock_llm_client):
        sections = {"data_overview": None, "sql_findings": None}
        result = await write_executive_summary(sections)
        assert result is None
        mock_llm_client.generate.assert_not_called()


class TestGenerateAllNarratives:
    """Test the full narrative generation pipeline."""

    @pytest.mark.asyncio
    async def test_full_bundle(self, full_bundle, mock_llm_client):
        result = await generate_all_narratives(full_bundle)
        assert result.data_overview is not None
        assert result.sql_findings is not None
        assert result.ml_insights is not None
        assert result.nlp_section is not None
        assert result.executive_summary is not None
        # 4 sections + 1 executive summary = 5 calls
        assert mock_llm_client.generate.call_count == 5

    @pytest.mark.asyncio
    async def test_minimal_bundle(self, minimal_bundle, mock_llm_client):
        result = await generate_all_narratives(minimal_bundle)
        assert result.data_overview is None
        assert result.sql_findings is None
        assert result.ml_insights is None
        assert result.nlp_section is None
        # No sections generated, so executive summary should also be None
        assert result.executive_summary is None
        assert mock_llm_client.generate.call_count == 0

    @pytest.mark.asyncio
    async def test_partial_bundle(self, partial_bundle, mock_llm_client):
        result = await generate_all_narratives(partial_bundle)
        assert result.data_overview is not None
        assert result.sql_findings is not None
        assert result.ml_insights is None
        assert result.nlp_section is None
        assert result.executive_summary is not None
        # 2 sections + 1 executive summary = 3 calls
        assert mock_llm_client.generate.call_count == 3
