"""
Shared test fixtures for Report Synthesis Agent tests.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.models import (
    AgentOutputBundle,
    ReportRequest,
    NarrativeSections,
    BrandingConfig,
)


@pytest.fixture
def sample_context_summary():
    return {
        "dataset_name": "sales_data_2024",
        "rows": 15000,
        "columns": 12,
        "column_types": {"numeric": 5, "categorical": 4, "datetime": 2, "text": 1},
        "missing_values": {"total_pct": 2.3, "columns_affected": ["discount", "region"]},
        "quality_score": 0.87,
    }


@pytest.fixture
def sample_sql_results():
    return [
        {"region": "North", "total_sales": 2500000, "avg_order": 350, "growth_pct": 12.5},
        {"region": "South", "total_sales": 1800000, "avg_order": 280, "growth_pct": -3.2},
        {"region": "East", "total_sales": 3100000, "avg_order": 420, "growth_pct": 18.7},
        {"region": "West", "total_sales": 2200000, "avg_order": 310, "growth_pct": 7.1},
    ]


@pytest.fixture
def sample_ml_results():
    return {
        "model_type": "Random Forest Classifier",
        "accuracy": 0.89,
        "f1_score": 0.86,
        "feature_importance": {
            "order_value": 0.32,
            "customer_tenure": 0.25,
            "region": 0.18,
            "product_category": 0.15,
            "discount_applied": 0.10,
        },
        "predictions": {"churn_risk_high": 234, "churn_risk_low": 1266},
    }


@pytest.fixture
def sample_nlp_insights():
    return {
        "sentiment": {"positive": 0.45, "neutral": 0.35, "negative": 0.20},
        "key_themes": ["product quality", "delivery speed", "customer support"],
        "entities": {"PRODUCT": 452, "LOCATION": 128, "PERSON": 67},
        "summary": "Customer feedback shows generally positive sentiment with delivery speed as the primary concern.",
    }


@pytest.fixture
def sample_charts():
    # Minimal valid 1x1 white PNG as base64
    return [
        {
            "title": "Sales by Region",
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
            "description": "Regional sales comparison chart",
        },
        {
            "title": "Trend Analysis",
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
            "description": "Monthly trend analysis",
        },
    ]


@pytest.fixture
def full_bundle(
    sample_context_summary,
    sample_sql_results,
    sample_ml_results,
    sample_nlp_insights,
    sample_charts,
):
    return AgentOutputBundle(
        context_summary=sample_context_summary,
        sql_results=sample_sql_results,
        charts=sample_charts,
        ml_results=sample_ml_results,
        nlp_insights=sample_nlp_insights,
        user_query="Analyze sales performance by region and predict churn risk",
        analysis_timestamp=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def minimal_bundle():
    return AgentOutputBundle(
        user_query="Simple analysis request",
        analysis_timestamp=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def partial_bundle(sample_context_summary, sample_sql_results):
    return AgentOutputBundle(
        context_summary=sample_context_summary,
        sql_results=sample_sql_results,
        user_query="Analyze the sales data",
        analysis_timestamp=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def sample_narratives():
    return NarrativeSections(
        data_overview=(
            "The sales dataset comprises 15,000 records across 12 fields, "
            "spanning four geographic regions. Data quality is high at 87%, "
            "with minor missing values in discount and region fields.\n\n"
            "The dataset includes numeric metrics such as sales totals and "
            "order values, alongside categorical attributes like region and "
            "product category, providing a comprehensive view of business performance."
        ),
        sql_findings=(
            "Regional analysis reveals the East region leading with $3.1M in sales "
            "and 18.7% growth, significantly outperforming other regions. The South "
            "region shows concerning negative growth at -3.2%.\n\n"
            "Average order values range from $280 (South) to $420 (East), suggesting "
            "the East region commands premium pricing. Overall growth is positive, "
            "but the South region requires strategic intervention."
        ),
        ml_insights=(
            "The Random Forest classifier achieved 89% accuracy in predicting customer "
            "churn, with order value and customer tenure as the strongest predictors. "
            "Of 1,500 customers analyzed, 234 were identified as high churn risk.\n\n"
            "The business should focus retention efforts on customers with low order "
            "values and short tenure, particularly in the South region where growth "
            "is already declining."
        ),
        nlp_section=(
            "Sentiment analysis of customer feedback shows 45% positive, 35% neutral, "
            "and 20% negative sentiment. Product quality and delivery speed emerged as "
            "the dominant themes in customer communications.\n\n"
            "Entity extraction identified 452 product mentions and 128 location references, "
            "indicating customers frequently discuss specific products and delivery destinations."
        ),
        executive_summary=(
            "The East region dominates performance with $3.1M in sales and 18.7% growth, "
            "while the South region faces declining growth at -3.2%. Machine learning "
            "analysis identified 234 high-risk churn customers, primarily characterized "
            "by low order values and short tenure. Customer sentiment is predominantly "
            "positive at 45%, with delivery speed as the key concern. Immediate action "
            "recommended: deploy targeted retention programs in the South region and "
            "address delivery speed issues to prevent further customer attrition."
        ),
    )


@pytest.fixture
def sample_branding():
    return BrandingConfig(
        company_name="Acme Analytics Corp",
        logo_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
        primary_color="#2563EB",
    )


@pytest.fixture
def mock_llm_client():
    """Mock LLM client that returns predictable responses."""
    with patch("app.narrative.llm_client") as mock:
        mock.generate = AsyncMock(
            return_value="This is a mock narrative section generated by the LLM."
        )
        yield mock


@pytest.fixture
def mock_redis():
    """Mock Redis for cache tests."""
    with patch("app.cache._get_redis") as mock:
        redis_mock = MagicMock()
        redis_mock.ping.return_value = True
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = True
        mock.return_value = redis_mock
        yield redis_mock
