"""Unit tests for the modern recommendation schema."""

import pytest
from pydantic import ValidationError

from src.eatsential.schemas.recommendation_schemas import (
    FeedbackRequest,
    FeedbackResponse,
    RecommendationFilters,
    RecommendationRequest,
    RecommendationResponse,
    RecommendedItem,
)


def test_recommended_item_has_explanation_field():
    """Ensure RecommendedItem includes an explanation string."""
    item = RecommendedItem(
        item_id="m_1",
        name="Protein Power Bowl",
        score=0.87,
        explanation="High protein, low allergen risk",
    )

    assert hasattr(item, "explanation")
    assert isinstance(item.explanation, str)
    assert item.explanation == "High protein, low allergen risk"


def test_recommendation_response_contains_items():
    """Ensure RecommendationResponse wraps recommended items with explanations."""
    item = RecommendedItem(
        item_id="m_1",
        name="Protein Power Bowl",
        score=0.87,
        explanation="High protein, low allergen risk",
    )
    resp = RecommendationResponse(items=[item])

    assert isinstance(resp.items, list)
    assert len(resp.items) == 1
    assert resp.items[0].explanation
    assert isinstance(resp.items[0].explanation, str)
    assert resp.items[0].explanation == "High protein, low allergen risk"


def test_recommended_item_explanation_non_empty():
    """Ensure explanation is a non-empty string."""
    item = RecommendedItem(
        item_id="m_2",
        name="Gut Friendly Salad",
        score=0.92,
        explanation="Matches your dietary preferences",
    )

    assert item.explanation
    assert len(item.explanation) > 0


def test_recommendation_filters_all_fields():
    """Test RecommendationFilters with all fields populated."""
    filters = RecommendationFilters(
        diet=["vegan", "gluten-free"],
        cuisine=["italian", "mediterranean"],
        price_range="$$",
    )

    assert filters.diet == ["vegan", "gluten-free"]
    assert filters.cuisine == ["italian", "mediterranean"]
    assert filters.price_range == "$$"


def test_recommendation_filters_all_optional():
    """Test RecommendationFilters with all fields as None (default)."""
    filters = RecommendationFilters()

    assert filters.diet is None
    assert filters.cuisine is None
    assert filters.price_range is None


def test_recommendation_filters_partial_fields():
    """Test RecommendationFilters with only some fields populated."""
    filters = RecommendationFilters(diet=["vegan"], price_range="$")

    assert filters.diet == ["vegan"]
    assert filters.cuisine is None
    assert filters.price_range == "$"


def test_recommendation_filters_empty_lists():
    """Test RecommendationFilters with empty lists."""
    filters = RecommendationFilters(diet=[], cuisine=[])

    assert filters.diet == []
    assert filters.cuisine == []


def test_recommendation_filters_single_item_lists():
    """Test RecommendationFilters with single-item lists."""
    filters = RecommendationFilters(diet=["vegetarian"], cuisine=["mexican"])

    assert filters.diet == ["vegetarian"]
    assert filters.cuisine == ["mexican"]



def test_recommendation_request_default_mode():
    """Test RecommendationRequest defaults to 'llm' mode."""
    request = RecommendationRequest()

    assert request.mode == "llm"
    assert request.filters is None


def test_recommendation_request_with_filters():
    """Test RecommendationRequest with filters."""
    filters = RecommendationFilters(diet=["vegan"])
    request = RecommendationRequest(filters=filters, mode="baseline")

    assert request.filters == filters
    assert request.mode == "baseline"


def test_recommendation_request_llm_mode():
    """Test RecommendationRequest with 'llm' mode."""
    request = RecommendationRequest(mode="llm")

    assert request.mode == "llm"


def test_recommendation_request_baseline_mode():
    """Test RecommendationRequest with 'baseline' mode."""
    request = RecommendationRequest(mode="baseline")

    assert request.mode == "baseline"


def test_recommendation_request_invalid_mode():
    """Test RecommendationRequest rejects invalid mode values."""
    with pytest.raises(ValidationError) as exc_info:
        RecommendationRequest(mode="invalid_mode")

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("llm" in str(error) or "baseline" in str(error) for error in errors)


def test_recommendation_request_none_mode():
    """Test RecommendationRequest with mode=None defaults to 'llm'."""
    request = RecommendationRequest(mode=None)

    assert request.mode == "llm"



def test_recommended_item_all_fields():
    """Test RecommendedItem with all required fields."""
    item = RecommendedItem(
        item_id="m_123",
        name="Test Meal",
        score=0.85,
        explanation="This is a test explanation",
    )

    assert item.item_id == "m_123"
    assert item.name == "Test Meal"
    assert item.score == 0.85
    assert item.explanation == "This is a test explanation"


def test_recommended_item_score_minimum():
    """Test RecommendedItem accepts minimum score of 0.0."""
    item = RecommendedItem(
        item_id="m_1",
        name="Low Score Item",
        score=0.0,
        explanation="Minimum score",
    )

    assert item.score == 0.0


def test_recommended_item_score_maximum():
    """Test RecommendedItem accepts maximum score of 1.0."""
    item = RecommendedItem(
        item_id="m_1",
        name="High Score Item",
        score=1.0,
        explanation="Maximum score",
    )

    assert item.score == 1.0


def test_recommended_item_score_below_minimum():
    """Test RecommendedItem rejects score below 0.0."""
    with pytest.raises(ValidationError) as exc_info:
        RecommendedItem(
            item_id="m_1",
            name="Invalid Item",
            score=-0.1,
            explanation="Negative score",
        )

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("greater than or equal to 0" in str(error).lower() for error in errors)


def test_recommended_item_score_above_maximum():
    """Test RecommendedItem rejects score above 1.0."""
    with pytest.raises(ValidationError) as exc_info:
        RecommendedItem(
            item_id="m_1",
            name="Invalid Item",
            score=1.1,
            explanation="Score too high",
        )

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("less than or equal to 1" in str(error).lower() for error in errors)


def test_recommended_item_missing_required_fields():
    """Test RecommendedItem requires all fields."""
    with pytest.raises(ValidationError):
        RecommendedItem(item_id="m_1", name="Test")  # Missing score and explanation

    with pytest.raises(ValidationError):
        RecommendedItem(item_id="m_1", score=0.5, explanation="Test")  # Missing name

    with pytest.raises(ValidationError):
        RecommendedItem(name="Test", score=0.5, explanation="Test")  # Missing item_id


def test_recommended_item_empty_strings():
    """Test RecommendedItem accepts empty strings (if needed)."""
    item = RecommendedItem(
        item_id="",
        name="",
        score=0.5,
        explanation="",
    )

    assert item.item_id == ""
    assert item.name == ""
    assert item.explanation == ""


def test_recommendation_response_empty_items():
    """Test RecommendationResponse with empty items list."""
    response = RecommendationResponse(items=[])

    assert isinstance(response.items, list)
    assert len(response.items) == 0


def test_recommendation_response_multiple_items():
    """Test RecommendationResponse with multiple items."""
    items = [
        RecommendedItem(
            item_id="m_1",
            name="Item 1",
            score=0.8,
            explanation="First item",
        ),
        RecommendedItem(
            item_id="m_2",
            name="Item 2",
            score=0.9,
            explanation="Second item",
        ),
        RecommendedItem(
            item_id="m_3",
            name="Item 3",
            score=0.7,
            explanation="Third item",
        ),
    ]

    response = RecommendationResponse(items=items)

    assert len(response.items) == 3
    assert response.items[0].item_id == "m_1"
    assert response.items[1].item_id == "m_2"
    assert response.items[2].item_id == "m_3"


def test_recommendation_response_missing_items():
    """Test RecommendationResponse requires items field."""
    with pytest.raises(ValidationError):
        RecommendationResponse()


def test_feedback_request_all_fields():
    """Test FeedbackRequest with all fields including notes."""
    request = FeedbackRequest(
        item_id="m_123",
        item_type="meal",
        feedback_type="like",
        notes="This meal was delicious!",
    )

    assert request.item_id == "m_123"
    assert request.item_type == "meal"
    assert request.feedback_type == "like"
    assert request.notes == "This meal was delicious!"


def test_feedback_request_without_notes():
    """Test FeedbackRequest without optional notes field."""
    request = FeedbackRequest(
        item_id="r_456",
        item_type="restaurant",
        feedback_type="dislike",
    )

    assert request.item_id == "r_456"
    assert request.item_type == "restaurant"
    assert request.feedback_type == "dislike"
    assert request.notes is None


def test_feedback_request_meal_type():
    """Test FeedbackRequest with 'meal' item_type."""
    request = FeedbackRequest(
        item_id="m_1",
        item_type="meal",
        feedback_type="like",
    )

    assert request.item_type == "meal"


def test_feedback_request_restaurant_type():
    """Test FeedbackRequest with 'restaurant' item_type."""
    request = FeedbackRequest(
        item_id="r_1",
        item_type="restaurant",
        feedback_type="dislike",
    )

    assert request.item_type == "restaurant"


def test_feedback_request_like_feedback():
    """Test FeedbackRequest with 'like' feedback_type."""
    request = FeedbackRequest(
        item_id="m_1",
        item_type="meal",
        feedback_type="like",
    )

    assert request.feedback_type == "like"


def test_feedback_request_dislike_feedback():
    """Test FeedbackRequest with 'dislike' feedback_type."""
    request = FeedbackRequest(
        item_id="m_1",
        item_type="meal",
        feedback_type="dislike",
    )

    assert request.feedback_type == "dislike"


def test_feedback_request_invalid_item_type():
    """Test FeedbackRequest rejects invalid item_type."""
    with pytest.raises(ValidationError) as exc_info:
        FeedbackRequest(
            item_id="m_1",
            item_type="invalid_type",
            feedback_type="like",
        )

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("meal" in str(error) or "restaurant" in str(error) for error in errors)


def test_feedback_request_invalid_feedback_type():
    """Test FeedbackRequest rejects invalid feedback_type."""
    with pytest.raises(ValidationError) as exc_info:
        FeedbackRequest(
            item_id="m_1",
            item_type="meal",
            feedback_type="invalid_feedback",
        )

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("like" in str(error) or "dislike" in str(error) for error in errors)


def test_feedback_request_missing_required_fields():
    """Test FeedbackRequest requires all mandatory fields."""
    with pytest.raises(ValidationError):
        FeedbackRequest(item_id="m_1", item_type="meal")  # Missing feedback_type

    with pytest.raises(ValidationError):
        FeedbackRequest(item_id="m_1", feedback_type="like")  # Missing item_type

    with pytest.raises(ValidationError):
        FeedbackRequest(item_type="meal", feedback_type="like")  # Missing item_id


def test_feedback_request_empty_notes():
    """Test FeedbackRequest with empty string notes."""
    request = FeedbackRequest(
        item_id="m_1",
        item_type="meal",
        feedback_type="like",
        notes="",
    )

    assert request.notes == ""


def test_feedback_response_all_fields():
    """Test FeedbackResponse with all fields."""
    response = FeedbackResponse(
        id="fb_123",
        item_id="m_456",
        item_type="meal",
        feedback_type="like",
        created_at="2024-01-15T10:30:00Z",
    )

    assert response.id == "fb_123"
    assert response.item_id == "m_456"
    assert response.item_type == "meal"
    assert response.feedback_type == "like"
    assert response.created_at == "2024-01-15T10:30:00Z"


def test_feedback_response_restaurant_type():
    """Test FeedbackResponse with restaurant item_type."""
    response = FeedbackResponse(
        id="fb_789",
        item_id="r_101",
        item_type="restaurant",
        feedback_type="dislike",
        created_at="2024-01-16T14:20:00Z",
    )

    assert response.item_type == "restaurant"
    assert response.feedback_type == "dislike"


def test_feedback_response_missing_required_fields():
    """Test FeedbackResponse requires all fields."""
    with pytest.raises(ValidationError):
        FeedbackResponse(
            id="fb_1",
            item_id="m_1",
            item_type="meal",
            # Missing feedback_type and created_at
        )


def test_feedback_response_string_types():
    """Test FeedbackResponse accepts string values for all fields."""
    response = FeedbackResponse(
        id="123",
        item_id="456",
        item_type="meal",
        feedback_type="like",
        created_at="2024-01-01",
    )

    assert isinstance(response.id, str)
    assert isinstance(response.item_id, str)
    assert isinstance(response.item_type, str)
    assert isinstance(response.feedback_type, str)
    assert isinstance(response.created_at, str)
