"""
Travel domain enhancer for purpose code classification.

This enhancer specializes in travel-related narrations and improves the classification
of travel-related purpose codes such as TRAD.
"""

import re
import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class TravelEnhancerSemantic(SemanticEnhancer):
    """
    Enhancer for travel-related narrations.

    This enhancer improves the classification of travel-related purpose codes by
    analyzing the narration for specific travel-related keywords and patterns.
    """

    def __init__(self, matcher=None):
        """
        Initialize with optional matcher.
        
        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)
        
        # Define travel-related keywords
        self.travel_keywords = [
            'travel', 'trip', 'journey', 'hotel', 'accommodation', 'lodging',
            'flight', 'airfare', 'airline', 'ticket', 'booking', 'reservation',
            'car rental', 'taxi', 'transportation', 'conference', 'exhibition',
            'tourism', 'vacation', 'holiday', 'tour', 'cruise', 'resort',
            'business trip', 'corporate travel', 'travel agency', 'itinerary'
        ]
        
        # Define travel-related patterns
        self.travel_patterns = [
            r'\b(travel|trip|journey)\b.*?\b(expense|payment|cost)\b',
            r'\b(expense|payment|cost)\b.*?\b(travel|trip|journey)\b',
            r'\b(pay(ing|ment)?|transfer(ing)?)\b.*?\b(for|to)\b.*?\b(travel|trip|journey)\b',
            r'\b(hotel|accommodation|lodging)\b.*?\b(payment|booking|reservation)\b',
            r'\b(payment|booking|reservation)\b.*?\b(hotel|accommodation|lodging)\b',
            r'\b(flight|airfare|airline)\b.*?\b(ticket|booking|reservation)\b',
            r'\b(car rental|taxi|transportation)\b.*?\b(service|payment)\b',
            r'\b(conference|exhibition|trade show)\b.*?\b(fee|payment|registration)\b',
            r'\b(business|corporate)\b.*?\b(travel|trip)\b',
            r'\b(travel|trip)\b.*?\b(business|corporate)\b',
            r'\b(travel agency|tour operator|airline|hotel chain)\b',
            r'\b(vacation|holiday|tour|cruise|resort)\b.*?\b(payment|booking|reservation)\b'
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.travel_patterns]
        
        # Initialize semantic terms for similarity matching
        self.semantic_terms = [
            {'term': 'travel', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'hotel', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'flight', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'accommodation', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'transportation', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'conference', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'business trip', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'vacation', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'tourism', 'purpose_code': 'TRAD', 'threshold': 0.7, 'weight': 1.0}
        ]
        
        # Initialize context patterns
        self.context_patterns = [
            {'purpose_code': 'TRAD', 'keywords': ['travel', 'expense'], 'proximity': 5, 'weight': 0.9},
            {'purpose_code': 'TRAD', 'keywords': ['hotel', 'payment'], 'proximity': 5, 'weight': 0.9},
            {'purpose_code': 'TRAD', 'keywords': ['flight', 'ticket'], 'proximity': 5, 'weight': 0.9},
            {'purpose_code': 'TRAD', 'keywords': ['business', 'trip'], 'proximity': 5, 'weight': 0.9},
            {'purpose_code': 'TRAD', 'keywords': ['conference', 'registration'], 'proximity': 5, 'weight': 0.9},
            {'purpose_code': 'TRAD', 'keywords': ['travel', 'agency'], 'proximity': 5, 'weight': 0.9},
            {'purpose_code': 'TRAD', 'keywords': ['car', 'rental'], 'proximity': 5, 'weight': 0.9},
            {'purpose_code': 'TRAD', 'keywords': ['vacation', 'package'], 'proximity': 5, 'weight': 0.9}
        ]
    
    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for travel-related transactions.
        
        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type
            
        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Travel enhancer called with narration: {narration}")
        
        # Get current purpose code and confidence
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)
        
        # Don't override if already classified with high confidence
        if confidence >= 0.8 and purpose_code != 'OTHR':
            logger.debug(f"Already classified with high confidence: {purpose_code} ({confidence:.2f})")
            return result
        
        # Check for travel patterns
        narration_lower = narration.lower()
        
        # Direct pattern matching
        for pattern in self.compiled_patterns:
            if pattern.search(narration):
                logger.info(f"Travel pattern matched: {pattern.pattern}")
                return self._create_enhanced_result(result, 'TRAD', 0.95, "travel_pattern_match")
        
        # Check for travel keywords
        for keyword in self.travel_keywords:
            if keyword in narration_lower:
                logger.info(f"Travel keyword match: {keyword} with confidence 0.90")
                enhanced_result = self._create_enhanced_result(result, 'TRAD', 0.90, f"travel_keyword_{keyword}")
                
                # Set category purpose code to TRAD
                enhanced_result['category_purpose_code'] = 'TRAD'
                enhanced_result['category_confidence'] = 0.90
                enhanced_result['category_enhancement_applied'] = "travel_category_mapping"
                
                return enhanced_result
        
        # Context pattern matching
        context_score = self.context_match(narration, self.context_patterns)
        if context_score >= 0.7:
            logger.info(f"Travel context match with score: {context_score:.2f}")
            enhanced_result = self._create_enhanced_result(result, 'TRAD', min(0.95, context_score), 
                                              f"Travel context match with score: {context_score:.2f}")
            
            # Set category purpose code to TRAD
            enhanced_result['category_purpose_code'] = 'TRAD'
            enhanced_result['category_confidence'] = min(0.95, context_score)
            enhanced_result['category_enhancement_applied'] = "travel_category_mapping"
            
            return enhanced_result
        
        # Semantic matching for travel-related terms
        matched, sem_confidence, sem_purpose_code, sem_matches = self.semantic_similarity_match(narration, self.semantic_terms)
        if matched and sem_purpose_code == 'TRAD':
            logger.info(f"Travel semantic match with confidence: {sem_confidence:.2f}")
            enhanced_result = self._create_enhanced_result(result, 'TRAD', sem_confidence, 
                                              f"Semantic similarity matches: {len(sem_matches)}")
            
            # Set category purpose code to TRAD
            enhanced_result['category_purpose_code'] = 'TRAD'
            enhanced_result['category_confidence'] = sem_confidence
            enhanced_result['category_enhancement_applied'] = "travel_category_mapping"
            
            return enhanced_result
        
        # Special handling for MT103 message type
        if message_type == 'MT103':
            # MT103 is commonly used for travel payments
            if any(term in narration_lower for term in ['travel', 'hotel', 'flight', 'accommodation']):
                logger.info(f"MT103 travel payment detected")
                enhanced_result = self._create_enhanced_result(result, 'TRAD', 0.85, "mt103_travel_payment")
                
                # Set category purpose code to TRAD
                enhanced_result['category_purpose_code'] = 'TRAD'
                enhanced_result['category_confidence'] = 0.85
                enhanced_result['category_enhancement_applied'] = "travel_category_mapping"
                
                return enhanced_result
        
        # Return original result if no enhancement applied
        return result
