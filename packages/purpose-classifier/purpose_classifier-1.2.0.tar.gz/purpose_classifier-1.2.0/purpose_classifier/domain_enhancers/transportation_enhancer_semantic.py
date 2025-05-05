"""
Transportation Domain Enhancer for Purpose Code Classifier

This enhancer specializes in identifying transportation-related payments
and improving classification accuracy for these types of transactions.
Uses advanced pattern matching with regular expressions and semantic understanding.
"""

import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
import logging

logger = logging.getLogger(__name__)

class TransportationDomainEnhancer(SemanticEnhancer):
    """
    Domain-specific enhancer for transportation-related payments.
    Helps reduce OTHR usage by identifying transportation payments.
    """

    def __init__(self, matcher=None):
        super().__init__(matcher=matcher)
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize semantic patterns and contexts."""
        # Direct keywords with purpose codes
        self.direct_keywords = {
            'TRANSPORTATION': ["freight payment", "shipping cost", "transportation fee", "logistics payment", "freight charges", "shipping payment", "transport service", "cargo payment", "freight invoice", "shipping invoice", "freight", "shipping", "transportation", "logistics", "cargo", "shipment", "delivery", "courier", "forwarding", "haulage", "trucking", "air freight", "sea freight", "rail transport", "container", "transport", "delivery", "shipment", "carrier", "transit", "express", "dispatch", "consignment", "load", "vessel", "truck", "air", "sea", "rail", "road"],
        }

        # Initialize transportation keywords with weights
        self.transportation_keywords = {
            "freight payment": 3.0,
            "shipping cost": 3.0,
            "transportation fee": 3.0,
            "logistics payment": 3.0,
            "freight charges": 3.0,
            "shipping payment": 3.0,
            "transport service": 2.5,
            "cargo payment": 3.0,
            "freight invoice": 3.0,
            "shipping invoice": 3.0,
            "freight": 2.0,
            "shipping": 2.0,
            "transportation": 2.0,
            "logistics": 1.5,
            "cargo": 2.0,
            "shipment": 2.0,
            "delivery": 1.5,
            "courier": 2.0,
            "forwarding": 2.0,
            "haulage": 2.5,
            "trucking": 2.5,
            "air freight": 2.5,
            "sea freight": 2.5,
            "rail transport": 2.5,
            "container": 1.5,
            "transport": 1.5,
            "carrier": 1.5,
            "transit": 1.5,
            "express": 1.5,
            "dispatch": 1.5,
            "consignment": 2.0,
            "load": 1.0,
            "vessel": 1.5,
            "truck": 1.5,
            "air": 1.0,
            "sea": 1.0,
            "rail": 1.0,
            "road": 1.0
        }

        # Initialize transportation purpose mappings
        self.transportation_purpose_mappings = {
            "freight payment": "TRPT",
            "shipping cost": "TRPT",
            "transportation fee": "TRPT",
            "logistics payment": "TRPT",
            "freight charges": "TRPT",
            "shipping payment": "TRPT",
            "transport service": "TRPT",
            "cargo payment": "TRPT",
            "freight invoice": "TRPT",
            "shipping invoice": "TRPT",
            "freight": "TRPT",
            "shipping": "TRPT",
            "transportation": "TRPT",
            "logistics": "TRPT",
            "cargo": "TRPT",
            "shipment": "TRPT",
            "delivery": "TRPT",
            "courier": "TRPT",
            "forwarding": "TRPT",
            "haulage": "TRPT",
            "trucking": "TRPT",
            "air freight": "TRPT",
            "sea freight": "TRPT",
            "rail transport": "TRPT"
        }

        # Initialize confidence thresholds
        self.confidence_thresholds = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.8
        }

        # Semantic context patterns
        self.context_patterns = [
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['freight', 'shipping', 'transportation', 'logistics', 'cargo', 'shipment', 'delivery', 'courier', 'forwarding', 'haulage', 'trucking', 'payment', 'cost', 'fee', 'charge', 'invoice', 'bill'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['payment', 'cost', 'fee', 'charge', 'invoice', 'bill', 'freight', 'shipping', 'transportation', 'logistics', 'cargo', 'shipment', 'delivery', 'courier', 'forwarding', 'haulage', 'trucking'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['pay', 'ing', 'ment', 'transfer', 'ing', 'for', 'freight', 'shipping', 'transportation', 'logistics', 'cargo', 'shipment', 'delivery', 'courier', 'forwarding', 'haulage', 'trucking'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['air', 'freight', 'air', 'cargo', 'air', 'shipment', 'air', 'transport', 'air', 'shipping', 'airway', 'bill', 'air', 'waybill', 'awb'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['air', 'freight', 'cargo', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['freight', 'cargo', 'shipment', 'transport', 'shipping', 'air'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['airline', 'airport', 'airways', 'aviation', 'freight', 'cargo', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['sea', 'freight', 'sea', 'cargo', 'sea', 'shipment', 'sea', 'transport', 'sea', 'shipping', 'ocean', 'freight', 'ocean', 'cargo', 'ocean', 'shipment', 'ocean', 'transport', 'ocean', 'shipping', 'maritime', 'freight', 'maritime', 'cargo', 'maritime', 'shipment', 'maritime', 'transport', 'maritime', 'shipping', 'bill', 'lading'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['sea', 'ocean', 'maritime', 'freight', 'cargo', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['freight', 'cargo', 'shipment', 'transport', 'shipping', 'sea', 'ocean', 'maritime'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['vessel', 'ship', 'container', 'port', 'harbor', 'harbour', 'dock', 'quay', 'pier', 'wharf', 'freight', 'cargo', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['rail', 'freight', 'rail', 'cargo', 'rail', 'shipment', 'rail', 'transport', 'rail', 'shipping', 'railway', 'freight', 'railway', 'cargo', 'railway', 'shipment', 'railway', 'transport', 'railway', 'shipping', 'train', 'freight', 'train', 'cargo', 'train', 'shipment', 'train', 'transport', 'train', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['rail', 'railway', 'train', 'freight', 'cargo', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['freight', 'cargo', 'shipment', 'transport', 'shipping', 'rail', 'railway', 'train'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['locomotive', 'wagon', 'carriage', 'track', 'station', 'freight', 'cargo', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['road', 'freight', 'road', 'cargo', 'road', 'shipment', 'road', 'transport', 'road', 'shipping', 'truck', 'freight', 'truck', 'cargo', 'truck', 'shipment', 'truck', 'transport', 'truck', 'shipping', 'lorry', 'freight', 'lorry', 'cargo', 'lorry', 'shipment', 'lorry', 'transport', 'lorry', 'shipping', 'haulage', 'trucking'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['road', 'truck', 'lorry', 'freight', 'cargo', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['freight', 'cargo', 'shipment', 'transport', 'shipping', 'road', 'truck', 'lorry'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['vehicle', 'trailer', 'driver', 'highway', 'motorway', 'freeway', 'freight', 'cargo', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['courier', 'service', 'courier', 'delivery', 'express', 'delivery', 'express', 'service', 'parcel', 'delivery', 'parcel', 'service', 'package', 'delivery', 'package', 'service', 'expedited', 'delivery', 'expedited', 'service', 'overnight', 'delivery', 'overnight', 'service', 'same', 'day', 'delivery', 'same', 'day', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['courier', 'express', 'parcel', 'package', 'delivery', 'service', 'shipment', 'transport', 'shipping'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['delivery', 'service', 'shipment', 'transport', 'shipping', 'courier', 'express', 'parcel', 'package'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['fedex', 'ups', 'dhl', 'tnt', 'usps', 'royal', 'mail', 'post', 'office', 'postal', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['freight', 'shipping', 'transportation', 'logistics', 'cargo', 'shipment', 'delivery', 'courier', 'forwarding', 'haulage', 'trucking'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
        ]

        # Semantic terms for similarity matching
        self.semantic_terms = []

    def score_transportation_relevance(self, text, message_type=None):
        """
        Score the relevance of the text to the transportation domain.
        Uses advanced pattern matching with regular expressions and semantic understanding.

        Args:
            text: The narration text
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            tuple: (score, matched_keywords, most_likely_purpose_code)
        """
        if not text:
            return 0.0, [], None

        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()

        # Initialize variables
        score = 0.0
        matched_keywords = []
        keyword_scores = {}
        pattern_matches = []

        # Check for each keyword with word boundary for more accurate matching
        for keyword, weight in self.transportation_keywords.items():
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += weight
                matched_keywords.append(keyword)
                keyword_scores[keyword] = weight
                logger.debug(f"Matched transportation keyword: {keyword} with weight {weight}")

        # Advanced pattern matching with semantic understanding
        # These patterns look for semantic relationships between words

        # Freight payment patterns
        freight_payment_patterns = [
            r'\b(freight|shipping|transportation|logistics|cargo|shipment|delivery|courier|forwarding|haulage|trucking)\b.*?\b(payment|cost|fee|charge|invoice|bill)\b',
            r'\b(payment|cost|fee|charge|invoice|bill)\b.*?\b(freight|shipping|transportation|logistics|cargo|shipment|delivery|courier|forwarding|haulage|trucking)\b',
            r'\b(pay(ing|ment)?|transfer(ing)?)\b.*?\b(for|to)\b.*?\b(freight|shipping|transportation|logistics|cargo|shipment|delivery|courier|forwarding|haulage|trucking)\b'
        ]

        for pattern in freight_payment_patterns:
            if re.search(pattern, text_lower):
                score += 3.0  # Higher weight for semantic patterns
                pattern_matches.append("freight_payment")
                logger.debug(f"Matched freight payment pattern: {pattern}")
                break  # Only count once

        # Air freight patterns
        air_freight_patterns = [
            r'\b(air\s+freight|air\s+cargo|air\s+shipment|air\s+transport|air\s+shipping|airway\s+bill|air\s+waybill|awb)\b',
            r'\b(air)\b.*?\b(freight|cargo|shipment|transport|shipping)\b',
            r'\b(freight|cargo|shipment|transport|shipping)\b.*?\b(air)\b',
            r'\b(airline|airport|airways|aviation)\b.*?\b(freight|cargo|shipment|transport|shipping)\b'
        ]

        for pattern in air_freight_patterns:
            if re.search(pattern, text_lower):
                score += 2.5  # Higher weight for semantic patterns
                pattern_matches.append("air_freight")
                logger.debug(f"Matched air freight pattern: {pattern}")
                break  # Only count once

        # Sea freight patterns
        sea_freight_patterns = [
            r'\b(sea\s+freight|sea\s+cargo|sea\s+shipment|sea\s+transport|sea\s+shipping|ocean\s+freight|ocean\s+cargo|ocean\s+shipment|ocean\s+transport|ocean\s+shipping|maritime\s+freight|maritime\s+cargo|maritime\s+shipment|maritime\s+transport|maritime\s+shipping|bill\s+of\s+lading|b\/l)\b',
            r'\b(sea|ocean|maritime)\b.*?\b(freight|cargo|shipment|transport|shipping)\b',
            r'\b(freight|cargo|shipment|transport|shipping)\b.*?\b(sea|ocean|maritime)\b',
            r'\b(vessel|ship|container|port|harbor|harbour|dock|quay|pier|wharf)\b.*?\b(freight|cargo|shipment|transport|shipping)\b'
        ]

        for pattern in sea_freight_patterns:
            if re.search(pattern, text_lower):
                score += 2.5  # Higher weight for semantic patterns
                pattern_matches.append("sea_freight")
                logger.debug(f"Matched sea freight pattern: {pattern}")
                break  # Only count once

        # Rail transport patterns
        rail_transport_patterns = [
            r'\b(rail\s+freight|rail\s+cargo|rail\s+shipment|rail\s+transport|rail\s+shipping|railway\s+freight|railway\s+cargo|railway\s+shipment|railway\s+transport|railway\s+shipping|train\s+freight|train\s+cargo|train\s+shipment|train\s+transport|train\s+shipping)\b',
            r'\b(rail|railway|train)\b.*?\b(freight|cargo|shipment|transport|shipping)\b',
            r'\b(freight|cargo|shipment|transport|shipping)\b.*?\b(rail|railway|train)\b',
            r'\b(locomotive|wagon|carriage|track|station)\b.*?\b(freight|cargo|shipment|transport|shipping)\b'
        ]

        for pattern in rail_transport_patterns:
            if re.search(pattern, text_lower):
                score += 2.5  # Higher weight for semantic patterns
                pattern_matches.append("rail_transport")
                logger.debug(f"Matched rail transport pattern: {pattern}")
                break  # Only count once

        # Road transport patterns
        road_transport_patterns = [
            r'\b(road\s+freight|road\s+cargo|road\s+shipment|road\s+transport|road\s+shipping|truck\s+freight|truck\s+cargo|truck\s+shipment|truck\s+transport|truck\s+shipping|lorry\s+freight|lorry\s+cargo|lorry\s+shipment|lorry\s+transport|lorry\s+shipping|haulage|trucking)\b',
            r'\b(road|truck|lorry)\b.*?\b(freight|cargo|shipment|transport|shipping)\b',
            r'\b(freight|cargo|shipment|transport|shipping)\b.*?\b(road|truck|lorry)\b',
            r'\b(vehicle|trailer|driver|highway|motorway|freeway)\b.*?\b(freight|cargo|shipment|transport|shipping)\b'
        ]

        for pattern in road_transport_patterns:
            if re.search(pattern, text_lower):
                score += 2.5  # Higher weight for semantic patterns
                pattern_matches.append("road_transport")
                logger.debug(f"Matched road transport pattern: {pattern}")
                break  # Only count once

        # Courier service patterns
        courier_patterns = [
            r'\b(courier\s+service|courier\s+delivery|express\s+delivery|express\s+service|parcel\s+delivery|parcel\s+service|package\s+delivery|package\s+service|expedited\s+delivery|expedited\s+service|overnight\s+delivery|overnight\s+service|same\s+day\s+delivery|same\s+day\s+service)\b',
            r'\b(courier|express|parcel|package)\b.*?\b(delivery|service|shipment|transport|shipping)\b',
            r'\b(delivery|service|shipment|transport|shipping)\b.*?\b(courier|express|parcel|package)\b',
            r'\b(fedex|ups|dhl|tnt|usps|royal\s+mail|post\s+office|postal\s+service)\b'
        ]

        for pattern in courier_patterns:
            if re.search(pattern, text_lower):
                score += 2.5  # Higher weight for semantic patterns
                pattern_matches.append("courier_service")
                logger.debug(f"Matched courier service pattern: {pattern}")
                break  # Only count once

        # Message type specific patterns
        if message_type == "MT103":
            # MT103 is commonly used for transportation payments
            if re.search(r'\b(freight|shipping|transportation|logistics|cargo|shipment|delivery|courier|forwarding|haulage|trucking)\b', text_lower):
                score += 1.0  # Boost for transportation terms in MT103
                pattern_matches.append("mt103_transportation_boost")
                logger.debug(f"Applied MT103 transportation boost")

        # Add pattern matches to matched keywords
        matched_keywords.extend(pattern_matches)

        # Normalize score to 0-1 range if we found matches
        if matched_keywords:
            # Lower denominator to make it easier to reach higher scores
            score = min(score / 4, 1.0)  # Cap at 1.0
            logger.debug(f"Transportation score: {score}")

        # Determine most likely purpose code based on matched keywords
        most_likely_purpose = None
        if matched_keywords:
            # First check for pattern matches which have higher priority
            if "freight_payment" in pattern_matches:
                most_likely_purpose = "TRPT"
            elif "air_freight" in pattern_matches:
                most_likely_purpose = "TRPT"
            elif "sea_freight" in pattern_matches:
                most_likely_purpose = "TRPT"
            elif "rail_transport" in pattern_matches:
                most_likely_purpose = "TRPT"
            elif "road_transport" in pattern_matches:
                most_likely_purpose = "TRPT"
            elif "courier_service" in pattern_matches:
                most_likely_purpose = "TRPT"
            else:
                # Sort matched keywords by their score (weight)
                sorted_keywords = sorted(
                    [(k, keyword_scores.get(k, 0)) for k in matched_keywords],
                    key=lambda x: x[1],
                    reverse=True
                )

                # Try to find a purpose code mapping for the highest-scored keywords
                for keyword, _ in sorted_keywords:
                    if keyword in self.transportation_purpose_mappings:
                        most_likely_purpose = self.transportation_purpose_mappings[keyword]
                        break

            # If no mapping found, default to TRPT
            if not most_likely_purpose:
                most_likely_purpose = "TRPT"

        return score, matched_keywords, most_likely_purpose

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification based on domain-specific knowledge for transportation domain.
        Uses advanced pattern matching with regular expressions and semantic understanding.

        Args:
            result: The classification result dictionary
            narration: The narration text
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            dict: The enhanced classification result
        """
        # Get message type from result if not provided
        if message_type is None and 'message_type' in result:
            message_type = result.get('message_type')

        # Get transportation relevance score, matched keywords, and most likely purpose code
        domain_score, matched_keywords, most_likely_purpose = self.score_transportation_relevance(narration, message_type)

        # Always add domain score and keywords to the result for analysis
        result['transportation_score'] = domain_score
        result['transportation_keywords'] = matched_keywords
        result['most_likely_transportation_purpose'] = most_likely_purpose

        # Skip enhancement if confidence is already high AND domain score isn't very high
        if result.get('confidence', 0.3) >= self.confidence_thresholds["high"]:
            # For high confidence results, don't change the purpose code
            return result

        # Lower threshold for applying enhancement - more aggressive to reduce OTHR usage
        if domain_score < 0.1 or not most_likely_purpose:
            return result

        # Original prediction and confidence
        original_purpose = result.get('purpose_code', 'OTHR')
        original_conf = result.get('confidence', 0.3)  # Default if not present

        # Message type specific considerations
        if message_type == "MT103":
            # MT103 is commonly used for transportation payments
            if "mt103_transportation_boost" in matched_keywords:
                # Boost domain score for MT103
                domain_score = min(domain_score * 1.2, 1.0)
                logger.debug(f"Boosted transportation score for MT103: {domain_score}")
                result['transportation_score'] = domain_score  # Update the score in the result

        # Determine if we need to override or enhance the classification
        if domain_score >= 0.25:
            # High domain relevance, determine the appropriate purpose code based on pattern matches
            purpose_code = most_likely_purpose  # Default to most likely purpose code
            enhancement_reason = None

            # Check for specific pattern matches to determine the purpose code
            if "freight_payment" in matched_keywords:
                purpose_code = "TRPT"
                enhancement_reason = "freight_payment_pattern"
            elif "air_freight" in matched_keywords:
                purpose_code = "TRPT"
                enhancement_reason = "air_freight_pattern"
            elif "sea_freight" in matched_keywords:
                purpose_code = "TRPT"
                enhancement_reason = "sea_freight_pattern"
            elif "rail_transport" in matched_keywords:
                purpose_code = "TRPT"
                enhancement_reason = "rail_transport_pattern"
            elif "road_transport" in matched_keywords:
                purpose_code = "TRPT"
                enhancement_reason = "road_transport_pattern"
            elif "courier_service" in matched_keywords:
                purpose_code = "TRPT"
                enhancement_reason = "courier_service_pattern"
            else:
                enhancement_reason = "high_transportation_score"

            # Apply the determined purpose code
            result['purpose_code'] = purpose_code

            # Blend original confidence with domain score - give more weight to domain_score
            adjusted_conf = (original_conf * 0.2) + (domain_score * 0.8)
            result['confidence'] = min(max(adjusted_conf, 0.7), 0.95)  # Minimum 0.7, cap at 0.95

            # Add enhancement info
            result['enhancement_applied'] = "transportation"
            result['enhanced'] = True
            result['enhancement_type'] = "transportation_domain_override"
            result['reason'] = enhancement_reason

            # Also enhance category purpose code if it's OTHR or not set
            if result.get('category_purpose_code') in ['OTHR', None, '']:
                result['category_purpose_code'] = "TRPT"
                result['category_confidence'] = result['confidence']
                result['category_enhancement_applied'] = "transportation_category_mapping"
                logger.debug(f"Set category purpose code to TRPT for transportation payment")

        # Medium domain relevance - enhance if original is OTHR or low confidence
        elif domain_score > 0.15:
            if original_purpose == 'OTHR' or original_conf < self.confidence_thresholds["medium"]:
                # Apply the most likely purpose code
                result['purpose_code'] = most_likely_purpose

                # Blend confidences but give less weight to domain score
                adjusted_conf = (original_conf * 0.4) + (domain_score * 0.6)
                result['confidence'] = min(adjusted_conf, 0.9)  # Cap at 0.9

                # Add enhancement info
                result['enhancement_applied'] = "transportation"
                result['enhanced'] = True
                result['enhancement_type'] = "transportation_domain_enhancement"
                result['reason'] = "medium_transportation_score"

                # Also enhance category purpose code if it's OTHR or not set
                if result.get('category_purpose_code') in ['OTHR', None, '']:
                    result['category_purpose_code'] = "TRPT"
                    result['category_confidence'] = result['confidence']
                    result['category_enhancement_applied'] = "transportation_category_mapping"
                    logger.debug(f"Set category purpose code to TRPT for transportation payment")
            else:
                # If original purpose is already TRPT, boost confidence slightly
                if original_purpose == 'TRPT':
                    result['confidence'] = min(original_conf * 1.2, 0.85)
                    result['enhancement_applied'] = "transportation"
                    result['enhanced'] = True
                    result['enhancement_type'] = "transportation_domain_minor_boost"
                    result['reason'] = "medium_transportation_score_with_trpt"

                    # Also enhance category purpose code if it's OTHR or not set
                    if result.get('category_purpose_code') in ['OTHR', None, '']:
                        result['category_purpose_code'] = "TRPT"
                        result['category_confidence'] = result['confidence']
                        result['category_enhancement_applied'] = "transportation_category_mapping"
                        logger.debug(f"Set category purpose code to TRPT for transportation payment")

        return result
