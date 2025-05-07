from abc import ABC, abstractmethod
from typing import Optional, List, Union
from dataclasses import dataclass
from mcard.config.config_constants import DEFAULT_PAGE_SIZE
from mcard.model.card import MCard
from mcard.model.g_time import GTime
from mcard.model.event_producer import generate_duplication_event, generate_collision_event, next_hash_function
import logging
import json

logger = logging.getLogger(__name__)

@dataclass
class Page:
    """A page of search results."""
    items: List[MCard]
    total_items: int
    page_number: int
    page_size: int
    has_next: bool
    has_previous: bool

class CardCollection:
    """High-level interface for card collection operations"""
    
    def __init__(self, engine):
        """Initialize with a specific database engine"""
        self.engine = engine
        
    def add(self, card: MCard) -> str:
        """Add a card to the collection.
        
        In a content-addressable scheme, we first check if there's an existing card
        with the same hash. If found, we compare the content to determine if it's
        a duplicate (same content) or a collision (different content).
        
        Args:
            card: The MCard to add
            
        Returns:
            str: The hash of the card
            
        Raises:
            ValueError: If card is None
        """
        logger.debug(f"Attempting to add card with content: {card.content}")
        if card is None:
            raise ValueError("Card cannot be None")
        
        # Get the hash of the incoming card
        hash_value = card.hash
        
        # Check if a card with this hash already exists
        existing_card = self.get(hash_value)
        if existing_card:
            logger.debug(f"Card with hash {hash_value} already exists")
            # Compare content to determine if it's a duplicate or collision
            if existing_card.content == card.content:
                logger.debug(f"Duplicate card found with content: {card.content}")
                # Same content = duplicate, create event and return original hash
                duplicate_event_content_str = generate_duplication_event(existing_card)
                duplicate_event_card = MCard(duplicate_event_content_str)
                self.add(duplicate_event_card)
                logger.debug(f"Added duplicate event card with hash: {duplicate_event_card.hash}")
                return duplicate_event_card.hash
            else:
                logger.debug(f"Collision detected for card with content: {card.content}")
                # Create collision event card and store the new card with new hash function
                collision_event_content_str = generate_collision_event(card)
                contentDict = json.loads(collision_event_content_str)
                # Different content = collision, upgrade hash function to stronger level
                collision_content_card = MCard(card.content, contentDict["upgraded_function"])  # Use the new hash function (upgraded_function)
                collision_event_card = MCard(collision_event_content_str)
                logger.debug(f"Collision event: {collision_event_content_str}")
                self.add(collision_event_card)
                self.add(collision_content_card)
                logger.debug(f"Added collision event card with hash: {collision_event_card.hash}")
                return collision_event_card.hash
        
        # No existing card with this hash or content, add the new card
        self.engine.add(card)
        logger.debug(f"Successfully added card with hash {hash_value}")
        return hash_value
        
    def get(self, hash_value: str) -> Optional[MCard]:
        """Retrieve a card by its hash"""
        return self.engine.get(hash_value)
        
    def delete(self, hash_value: str) -> bool:
        """Delete a card by its hash"""
        return self.engine.delete(hash_value)
        
    def get_page(self, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Get a page of cards"""
        return self.engine.get_page(page_number, page_size)
        
    def search_by_string(self, search_string: str, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        # Delegate the search to the engine's search_by_string method
        return self.engine.search_by_string(search_string, page_number, page_size)
        
    def search_by_hash(self, hash_value: str, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Search for cards by hash value"""
        if not hash_value:
            raise ValueError("Hash value cannot be empty")
        if page_number < 1:
            raise ValueError("Page number must be greater than 0")
        if page_size < 1:
            raise ValueError("Page size must be greater than 0")
        
        # Get all matching cards
        matching_cards = []
        for card in self.engine.get_all().items:  # Accessing the items from the Page object
            if str(card.hash) == hash_value:
                matching_cards.append(card)
        
        # Calculate pagination
        total_items = len(matching_cards)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        items = matching_cards[start_idx:end_idx]
        
        # Create page object
        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=end_idx < total_items,
            has_previous=page_number > 1
        )
        
    def search_by_content(self, search_string: str, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Search for cards by content string"""
        return self.engine.search_by_content(search_string, page_number, page_size)

        
    def clear(self) -> None:
        """Remove all cards"""
        self.engine.clear()
        
    def count(self) -> int:
        """Return total number of cards"""
        return self.engine.count()

    def get_all(self) -> Page:
        """Return all cards"""
        return self.engine.get_all()

    def get_all_cards(self, page_number: int = 1, page_size: int = 10) -> Page:
        return self.engine.get_all(page_number=page_number, page_size=page_size)