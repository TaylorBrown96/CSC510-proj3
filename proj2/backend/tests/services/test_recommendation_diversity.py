"""Unit tests for recommendation diversity feature.

Tests the _ensure_diverse_restaurants method and diversity logic across
meal and restaurant recommendations.
"""

import pytest
from unittest.mock import Mock
from eatsential.services.engine import RecommendationService
from eatsential.schemas.recommendation_schemas import RecommendedItem


class TestRecommendationDiversity:
    """Test suite for recommendation diversity functionality."""

    def test_ensure_diverse_restaurants_basic(self):
        """Test basic diversity filtering with multiple restaurants."""
        service = RecommendationService(db=Mock())
        
        # Create 6 items: 3 from restaurant A, 2 from B, 1 from C
        items = [
            RecommendedItem(
                item_id="1", name="Item 1", score=0.9, explanation="Test",
                restaurant_place_id="rest_a", restaurant_name="Restaurant A"
            ),
            RecommendedItem(
                item_id="2", name="Item 2", score=0.8, explanation="Test",
                restaurant_place_id="rest_a", restaurant_name="Restaurant A"
            ),
            RecommendedItem(
                item_id="3", name="Item 3", score=0.7, explanation="Test",
                restaurant_place_id="rest_b", restaurant_name="Restaurant B"
            ),
            RecommendedItem(
                item_id="4", name="Item 4", score=0.6, explanation="Test",
                restaurant_place_id="rest_a", restaurant_name="Restaurant A"
            ),
            RecommendedItem(
                item_id="5", name="Item 5", score=0.5, explanation="Test",
                restaurant_place_id="rest_b", restaurant_name="Restaurant B"
            ),
            RecommendedItem(
                item_id="6", name="Item 6", score=0.4, explanation="Test",
                restaurant_place_id="rest_c", restaurant_name="Restaurant C"
            ),
        ]
        
        # Apply diversity filter (max 2 per restaurant by default)
        diverse = service._ensure_diverse_restaurants(items)
        
        # Should get interleaved results: A1, B1, C1, A2, B2 (max 2 per restaurant)
        assert len(diverse) == 5
        
        # Count items per restaurant
        rest_counts = {}
        for item in diverse:
            rest_id = item.restaurant_place_id
            rest_counts[rest_id] = rest_counts.get(rest_id, 0) + 1
        
        # No restaurant should have more than 2 items
        assert all(count <= 2 for count in rest_counts.values())
        assert rest_counts["rest_a"] == 2
        assert rest_counts["rest_b"] == 2
        assert rest_counts["rest_c"] == 1

    def test_ensure_diverse_restaurants_interleaving(self):
        """Test that restaurants are properly interleaved."""
        service = RecommendationService(db=Mock())
        
        # Create items from 2 restaurants
        items = [
            RecommendedItem(
                item_id="a1", name="A1", score=0.9, explanation="Test",
                restaurant_place_id="rest_a", restaurant_name="Restaurant A"
            ),
            RecommendedItem(
                item_id="a2", name="A2", score=0.8, explanation="Test",
                restaurant_place_id="rest_a", restaurant_name="Restaurant A"
            ),
            RecommendedItem(
                item_id="b1", name="B1", score=0.7, explanation="Test",
                restaurant_place_id="rest_b", restaurant_name="Restaurant B"
            ),
            RecommendedItem(
                item_id="b2", name="B2", score=0.6, explanation="Test",
                restaurant_place_id="rest_b", restaurant_name="Restaurant B"
            ),
        ]
        
        diverse = service._ensure_diverse_restaurants(items)
        
        # Should be interleaved: A1, B1, A2, B2
        assert len(diverse) == 4
        assert diverse[0].restaurant_place_id == "rest_a"
        assert diverse[1].restaurant_place_id == "rest_b"
        assert diverse[2].restaurant_place_id == "rest_a"
        assert diverse[3].restaurant_place_id == "rest_b"

    def test_ensure_diverse_restaurants_single_restaurant(self):
        """Test behavior when all items are from same restaurant."""
        service = RecommendationService(db=Mock())
        
        items = [
            RecommendedItem(
                item_id=str(i), name=f"Item {i}", score=0.9 - i*0.1,
                explanation="Test", restaurant_place_id="rest_a",
                restaurant_name="Restaurant A"
            )
            for i in range(5)
        ]
        
        diverse = service._ensure_diverse_restaurants(items)
        
        # All from same restaurant, limited by max_same_restaurant (default = 2)
        assert len(diverse) == 2
        assert all(item.restaurant_place_id == "rest_a" for item in diverse)

    def test_ensure_diverse_restaurants_custom_max(self):
        """Test custom max_same_restaurant parameter."""
        service = RecommendationService(db=Mock())
        
        items = [
            RecommendedItem(
                item_id=str(i), name=f"Item {i}", score=0.9 - i*0.1,
                explanation="Test", restaurant_place_id="rest_a",
                restaurant_name="Restaurant A"
            )
            for i in range(5)
        ]
        
        # Limit to only 1 item per restaurant
        diverse = service._ensure_diverse_restaurants(items, max_same_restaurant=1)
        
        assert len(diverse) == 1
        assert diverse[0].item_id == "0"  # Should get highest score

    def test_ensure_diverse_restaurants_none_place_ids(self):
        """Test handling of items with None place_ids."""
        service = RecommendationService(db=Mock())
        
        items = [
            RecommendedItem(
                item_id="1", name="Item 1", score=0.9, explanation="Test",
                restaurant_place_id=None, restaurant_name="Restaurant A"
            ),
            RecommendedItem(
                item_id="2", name="Item 2", score=0.8, explanation="Test",
                restaurant_place_id="rest_b", restaurant_name="Restaurant B"
            ),
        ]
        
        diverse = service._ensure_diverse_restaurants(items)
        
        # Should handle None gracefully
        assert len(diverse) == 2

    def test_ensure_diverse_restaurants_empty_list(self):
        """Test with empty input list."""
        service = RecommendationService(db=Mock())
        
        diverse = service._ensure_diverse_restaurants([])
        
        assert diverse == []

    def test_ensure_diverse_restaurants_single_item(self):
        """Test with single item."""
        service = RecommendationService(db=Mock())
        
        items = [
            RecommendedItem(
                item_id="1", name="Item 1", score=0.9, explanation="Test",
                restaurant_place_id="rest_a", restaurant_name="Restaurant A"
            )
        ]
        
        diverse = service._ensure_diverse_restaurants(items)
        
        assert len(diverse) == 1
        assert diverse[0].item_id == "1"

    def test_ensure_diverse_restaurants_many_restaurants(self):
        """Test with many different restaurants (more than needed)."""
        service = RecommendationService(db=Mock())
        
        # Create 10 items from 10 different restaurants
        items = [
            RecommendedItem(
                item_id=str(i), name=f"Item {i}", score=0.9 - i*0.05,
                explanation="Test", restaurant_place_id=f"rest_{i}",
                restaurant_name=f"Restaurant {i}"
            )
            for i in range(10)
        ]
        
        diverse = service._ensure_diverse_restaurants(items)
        
        # Should get all 10 items (one per restaurant)
        assert len(diverse) == 10
        
        # All should have different place_ids
        place_ids = [item.restaurant_place_id for item in diverse]
        assert len(set(place_ids)) == 10

    def test_diversity_preserves_score_ordering_within_restaurant(self):
        """Test that items from same restaurant maintain score order."""
        service = RecommendationService(db=Mock())
        
        items = [
            RecommendedItem(
                item_id="a1", name="A High", score=0.9, explanation="Test",
                restaurant_place_id="rest_a", restaurant_name="Restaurant A"
            ),
            RecommendedItem(
                item_id="b1", name="B High", score=0.85, explanation="Test",
                restaurant_place_id="rest_b", restaurant_name="Restaurant B"
            ),
            RecommendedItem(
                item_id="a2", name="A Low", score=0.7, explanation="Test",
                restaurant_place_id="rest_a", restaurant_name="Restaurant A"
            ),
            RecommendedItem(
                item_id="b2", name="B Low", score=0.6, explanation="Test",
                restaurant_place_id="rest_b", restaurant_name="Restaurant B"
            ),
        ]
        
        diverse = service._ensure_diverse_restaurants(items)
        
        # Should maintain score order within each restaurant
        # A items: a1 (0.9) should come before a2 (0.7)
        # B items: b1 (0.85) should come before b2 (0.6)
        a_items = [item for item in diverse if item.restaurant_place_id == "rest_a"]
        b_items = [item for item in diverse if item.restaurant_place_id == "rest_b"]
        
        if len(a_items) > 1:
            assert a_items[0].score > a_items[1].score
        if len(b_items) > 1:
            assert b_items[0].score > b_items[1].score
