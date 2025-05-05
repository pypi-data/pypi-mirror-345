"""
TechDomainEnhancer for Purpose Code Classifier

This enhancer specializes in identifying technology and software-related payments
and improving classification accuracy for these types of transactions.
Uses advanced pattern matching with regular expressions and semantic understanding.
"""

import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
import logging

logger = logging.getLogger(__name__)

class TechDomainEnhancer(SemanticEnhancer):
    """Enhances classification for software development and IT services payments"""

    def __init__(self, matcher=None):
        super().__init__(matcher=matcher)
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize semantic patterns and contexts."""
        # Direct keywords with purpose codes
        self.direct_keywords = {
            'TECH': ["software development", "software engineering", "programming", "coding", "development services", "app development", "application development", "web development", "mobile development", "software service", "software services", "platform migration", "enterprise platform", "migration project", "it services", "information technology", "system integration", "cloud services", "software implementation", "technical support", "software maintenance", "software support", "it consulting", "system upgrade", "tech solution", "implementation service", "software license", "software subscription", "saas", "software as a service", "api", "platform", "software solution", "database", "hosting", "server", "infrastructure", "cloud platform", "enterprise software", "sprint", "milestone", "release", "deployment", "phase", "agile", "scrum", "project", "development phase", "migration", "implementation", "contract ref", "invoice"],
        }

        # Initialize tech keywords with weights
        self.tech_keywords = {
            "software development": 3.0,
            "software engineering": 3.0,
            "programming": 2.5,
            "coding": 2.5,
            "development services": 2.5,
            "app development": 3.0,
            "application development": 3.0,
            "web development": 3.0,
            "mobile development": 3.0,
            "software service": 2.5,
            "software services": 2.5,
            "platform migration": 2.0,
            "enterprise platform": 2.0,
            "migration project": 2.0,
            "it services": 2.5,
            "information technology": 2.5,
            "system integration": 2.5,
            "cloud services": 2.5,
            "software implementation": 2.5,
            "technical support": 2.0,
            "software maintenance": 2.0,
            "software support": 2.0,
            "it consulting": 2.5,
            "system upgrade": 2.0,
            "tech solution": 2.0,
            "implementation service": 2.0,
            "software license": 3.0,
            "software subscription": 3.0,
            "saas": 3.0,
            "software as a service": 3.0,
            "api": 2.0,
            "platform": 1.5,
            "software solution": 2.0,
            "database": 1.5,
            "hosting": 1.5,
            "server": 1.5,
            "infrastructure": 1.5,
            "cloud platform": 2.0,
            "enterprise software": 2.5,
            "sprint": 1.5,
            "milestone": 1.5,
            "release": 1.5,
            "deployment": 1.5,
            "phase": 1.0,
            "agile": 1.5,
            "scrum": 1.5,
            "project": 1.0,
            "development phase": 1.5,
            "migration": 1.5,
            "implementation": 1.5,
            "contract ref": 1.0,
            "invoice": 0.5
        }

        # Initialize word triggers with weights
        self.word_triggers = {
            "software": 1.0,
            "application": 0.8,
            "app": 0.8,
            "development": 0.7,
            "programming": 1.0,
            "coding": 1.0,
            "web": 0.6,
            "mobile": 0.6,
            "platform": 0.7,
            "cloud": 0.7,
            "api": 0.8,
            "database": 0.7,
            "server": 0.7,
            "hosting": 0.7,
            "infrastructure": 0.7,
            "implementation": 0.6,
            "integration": 0.7,
            "migration": 0.7,
            "sprint": 0.8,
            "agile": 0.8,
            "scrum": 0.8,
            "milestone": 0.7,
            "release": 0.7,
            "deployment": 0.7,
            "license": 0.8,
            "subscription": 0.7,
            "saas": 1.0,
            "technical": 0.6,
            "support": 0.5,
            "maintenance": 0.5,
            "consulting": 0.6,
            "solution": 0.5,
            "enterprise": 0.6,
            "system": 0.5,
            "upgrade": 0.6,
            "project": 0.5,
            "phase": 0.5,
            "tech": 0.7,
            "it": 0.6
        }

        # Initialize transportation purpose mappings
        self.transportation_purpose_mappings = {
            "software development": "SCVE",
            "software engineering": "SCVE",
            "programming": "SCVE",
            "coding": "SCVE",
            "development services": "SCVE",
            "app development": "SCVE",
            "application development": "SCVE",
            "web development": "SCVE",
            "mobile development": "SCVE",
            "software service": "SCVE",
            "software services": "SCVE",
            "platform migration": "SCVE",
            "enterprise platform": "SCVE",
            "migration project": "SCVE",
            "it services": "SCVE",
            "information technology": "SCVE",
            "system integration": "SCVE",
            "cloud services": "SCVE",
            "software implementation": "SCVE",
            "technical support": "SCVE",
            "software maintenance": "SCVE",
            "software support": "SCVE",
            "it consulting": "SCVE",
            "system upgrade": "SCVE",
            "tech solution": "SCVE",
            "implementation service": "SCVE",
            "software license": "LICF",
            "software subscription": "SUBS",
            "saas": "SUBS",
            "software as a service": "SUBS"
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
                'keywords': ['software', 'application', 'app', 'web', 'mobile', 'development', 'engineering', 'programming', 'coding'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['development', 'engineering', 'programming', 'coding', 'software', 'application', 'app', 'web', 'mobile'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['develop', 'create', 'build', 'code', 'program', 'software', 'application', 'app', 'web', 'mobile'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['software', 'application', 'app', 'web', 'mobile', 'develop', 'create', 'build', 'code', 'program'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['information', 'technology', 'tech', 'service', 'support', 'consulting', 'maintenance'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'support', 'consulting', 'maintenance', 'information', 'technology', 'tech'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['system', 'cloud', 'network', 'infrastructure', 'integration', 'implementation', 'migration', 'upgrade'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['integration', 'implementation', 'migration', 'upgrade', 'system', 'cloud', 'network', 'infrastructure'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['software', 'application', 'app', 'platform', 'license', 'subscription', 'renewal', 'activation'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['license', 'subscription', 'renewal', 'activation', 'software', 'application', 'app', 'platform'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['saas', 'software', 'service', 'cloud', 'service', 'subscription', 'fee', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['subscription', 'fee', 'payment', 'saas', 'software', 'service', 'cloud', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['platform', 'infrastructure', 'server', 'database', 'hosting', 'service', 'maintenance', 'support', 'management'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'maintenance', 'support', 'management', 'platform', 'infrastructure', 'server', 'database', 'hosting'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['cloud', 'enterprise', 'digital', 'platform', 'infrastructure', 'solution', 'environment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['platform', 'infrastructure', 'solution', 'environment', 'cloud', 'enterprise', 'digital'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['project', 'sprint', 'milestone', 'phase', 'release', 'deployment', 'software', 'development', 'implementation', 'migration'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['software', 'development', 'implementation', 'migration', 'project', 'sprint', 'milestone', 'phase', 'release', 'deployment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['agile', 'scrum', 'waterfall', 'development', 'methodology', 'process', 'project'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['development', 'methodology', 'process', 'project', 'agile', 'scrum', 'waterfall'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['software', 'tech', 'development', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['subscription', 'saas', 'software', 'service'],
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
                'purpose_code': 'SCVE',
                'keywords': ['subscription', 'saas', 'software', 'service'],
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

    def score_tech_relevance(self, narration, message_type=None):
        """
        Score how relevant a narration is to tech/software domain
        Returns a score and list of matched keywords

        Args:
            narration: The narration text
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            tuple: (score, matched_keywords)
        """
        if not narration:
            return 0, []

        narration_lower = narration.lower()
        score = 0
        matched_keywords = []
        pattern_matches = []

        # 1. First check for exact phrase matches (highest confidence)
        for keyword, weight in self.tech_keywords.items():
            # Use word boundary regex pattern for more accurate matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, narration_lower, re.IGNORECASE):
                score += weight * 2  # Double the weight to make it more likely to pass the threshold
                matched_keywords.append(keyword)
                logger.debug(f"Matched tech keyword: {keyword} with weight {weight * 2}")

        # 2. Check for individual word triggers if no strong matches yet
        # Only apply if we don't have a strong match already (score < 2)
        if score < 2:
            words = set(re.findall(r'\b\w+\b', narration_lower))
            for word, weight in self.word_triggers.items():
                if word in words:
                    score += weight
                    matched_keywords.append(f"word:{word}")
                    logger.debug(f"Matched word trigger: {word} with weight {weight}")

        # 3. Advanced pattern matching with semantic understanding
        # These patterns look for semantic relationships between words

        # Software development patterns
        software_dev_patterns = [
            r'\b(software|application|app|web|mobile)\b.*?\b(development|engineering|programming|coding)\b',
            r'\b(development|engineering|programming|coding)\b.*?\b(software|application|app|web|mobile)\b',
            r'\b(develop|create|build|code|program)\b.*?\b(software|application|app|web|mobile)\b',
            r'\b(software|application|app|web|mobile)\b.*?\b(develop|create|build|code|program)\b'
        ]

        for pattern in software_dev_patterns:
            if re.search(pattern, narration_lower):
                score += 3.0  # Higher weight for semantic patterns
                pattern_matches.append("software_development")
                logger.debug(f"Matched software development pattern: {pattern}")
                break  # Only count once

        # IT services patterns
        it_services_patterns = [
            r'\b(it|information\s+technology|tech)\b.*?\b(service|support|consulting|maintenance)\b',
            r'\b(service|support|consulting|maintenance)\b.*?\b(it|information\s+technology|tech)\b',
            r'\b(system|cloud|network|infrastructure)\b.*?\b(integration|implementation|migration|upgrade)\b',
            r'\b(integration|implementation|migration|upgrade)\b.*?\b(system|cloud|network|infrastructure)\b'
        ]

        for pattern in it_services_patterns:
            if re.search(pattern, narration_lower):
                score += 2.5  # Higher weight for semantic patterns
                pattern_matches.append("it_services")
                logger.debug(f"Matched IT services pattern: {pattern}")
                break  # Only count once

        # Software license patterns
        software_license_patterns = [
            r'\b(software|application|app|platform)\b.*?\b(license|subscription|renewal|activation)\b',
            r'\b(license|subscription|renewal|activation)\b.*?\b(software|application|app|platform)\b',
            r'\b(saas|software\s+as\s+a\s+service|cloud\s+service)\b.*?\b(subscription|fee|payment)\b',
            r'\b(subscription|fee|payment)\b.*?\b(saas|software\s+as\s+a\s+service|cloud\s+service)\b'
        ]

        for pattern in software_license_patterns:
            if re.search(pattern, narration_lower):
                score += 2.0  # Higher weight for semantic patterns
                pattern_matches.append("software_license")
                logger.debug(f"Matched software license pattern: {pattern}")
                break  # Only count once

        # Platform and infrastructure patterns
        platform_patterns = [
            r'\b(platform|infrastructure|server|database|hosting)\b.*?\b(service|maintenance|support|management)\b',
            r'\b(service|maintenance|support|management)\b.*?\b(platform|infrastructure|server|database|hosting)\b',
            r'\b(cloud|enterprise|digital)\b.*?\b(platform|infrastructure|solution|environment)\b',
            r'\b(platform|infrastructure|solution|environment)\b.*?\b(cloud|enterprise|digital)\b'
        ]

        for pattern in platform_patterns:
            if re.search(pattern, narration_lower):
                score += 2.0  # Higher weight for semantic patterns
                pattern_matches.append("platform_infrastructure")
                logger.debug(f"Matched platform/infrastructure pattern: {pattern}")
                break  # Only count once

        # Project-related patterns
        project_patterns = [
            r'\b(project|sprint|milestone|phase|release|deployment)\b.*?\b(software|development|implementation|migration)\b',
            r'\b(software|development|implementation|migration)\b.*?\b(project|sprint|milestone|phase|release|deployment)\b',
            r'\b(agile|scrum|waterfall)\b.*?\b(development|methodology|process|project)\b',
            r'\b(development|methodology|process|project)\b.*?\b(agile|scrum|waterfall)\b',
            r'\btech\s+project\b',  # Add direct match for "tech project"
            r'\btechnology\s+project\b',
            r'\bit\s+project\b'
        ]

        for pattern in project_patterns:
            if re.search(pattern, narration_lower):
                score += 3.0  # Higher weight for semantic patterns
                pattern_matches.append("tech_project")
                pattern_matches.append("software_development")  # Add this to ensure it gets classified as SCVE
                logger.debug(f"Matched tech project pattern: {pattern}")
                break  # Only count once

        # Message type specific patterns
        if message_type == "MT103":
            # MT103 is commonly used for software and IT service payments
            if re.search(r'\b(software|it|tech|development|service)\b', narration_lower):
                score += 3.0  # Boost for tech terms in MT103
                pattern_matches.append("mt103_tech_boost")
                pattern_matches.append("software_development")  # Add this to ensure it gets classified as SCVE
                logger.debug(f"Applied MT103 tech boost")

        # Add pattern matches to matched keywords
        matched_keywords.extend(pattern_matches)

        # Normalize score to 0-1 range if we found matches
        if matched_keywords:
            # Lower denominator to make it easier to reach higher scores (8 instead of 10)
            score = min(score / 8, 1.0)  # Cap at 1.0
            logger.debug(f"Tech score: {score}")

        return score, matched_keywords

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification based on domain-specific knowledge for tech domain.
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

        # Get tech relevance score and matched keywords first
        tech_score, matched_keywords = self.score_tech_relevance(narration, message_type)

        # Always add tech score and keywords to the result for analysis
        result['tech_score'] = tech_score
        result['tech_keywords'] = matched_keywords

        # Skip enhancement if confidence is already high
        # This prevents overriding high confidence results
        if result.get('confidence', 0.3) >= self.confidence_thresholds["high"]:
            # For high confidence results, don't change the purpose code
            return result

        # Lower threshold for applying enhancement (from 0.3 to 0.2)
        # This makes it more sensitive to tech-related terms
        if tech_score < 0.2:
            return result

        # Original prediction and confidence
        original_purpose = result.get('purpose_code', 'OTHR')
        original_conf = result.get('confidence', 0.3)

        # Message type specific considerations
        if message_type == "MT103":
            # MT103 is commonly used for software and IT service payments
            if "mt103_tech_boost" in matched_keywords:
                # Boost tech score for MT103
                tech_score = min(tech_score * 1.2, 1.0)
                logger.debug(f"Boosted tech score for MT103: {tech_score}")
                result['tech_score'] = tech_score  # Update the score in the result

        # Determine if we need to override or enhance the classification
        # Lower threshold from 0.5 to 0.3 for high tech relevance
        if tech_score > 0.3:
            # High tech relevance, determine the appropriate purpose code based on pattern matches
            purpose_code = "SCVE"  # Default to SCVE (Purchase of Services)
            purpose_description = "Purchase of Services"
            enhancement_reason = None

            # Check for specific pattern matches to determine the purpose code
            if "software_license" in matched_keywords:
                # Check if it's a subscription or license
                if re.search(r'\b(subscription|saas|software\s+as\s+a\s+service)\b', narration.lower()):
                    purpose_code = "SUBS"
                    purpose_description = "Subscription"
                    enhancement_reason = "software_subscription_pattern"
                else:
                    purpose_code = "LICF"
                    purpose_description = "License Fee"
                    enhancement_reason = "software_license_pattern"
            elif "software_development" in matched_keywords:
                purpose_code = "SCVE"
                purpose_description = "Purchase of Services"
                enhancement_reason = "software_development_pattern"
            elif "it_services" in matched_keywords:
                purpose_code = "SCVE"
                purpose_description = "Purchase of Services"
                enhancement_reason = "it_services_pattern"
            elif "platform_infrastructure" in matched_keywords:
                # Check if it's a subscription or service
                if re.search(r'\b(subscription|saas|software\s+as\s+a\s+service)\b', narration.lower()):
                    purpose_code = "SUBS"
                    purpose_description = "Subscription"
                    enhancement_reason = "platform_subscription_pattern"
                else:
                    purpose_code = "SCVE"
                    purpose_description = "Purchase of Services"
                    enhancement_reason = "platform_service_pattern"
            elif "tech_project" in matched_keywords:
                purpose_code = "SCVE"
                purpose_description = "Purchase of Services"
                enhancement_reason = "tech_project_pattern"
            else:
                enhancement_reason = "high_tech_score"

            # Apply the determined purpose code
            result['purpose_code'] = purpose_code
            result['purpose_description'] = purpose_description

            # Blend original confidence with tech score - give more weight to tech_score
            adjusted_conf = (original_conf * 0.2) + (tech_score * 0.8)
            result['confidence'] = min(max(adjusted_conf, 0.7), 0.95)  # Minimum 0.7, cap at 0.95

            # Add enhancement info
            result['enhancer'] = "tech"
            result['enhanced'] = True
            result['reason'] = f"Tech domain match: {enhancement_reason}"

            # Also enhance category purpose code mapping
            if purpose_code == "LICF":
                result['category_purpose_code'] = "LICF"
                result['category_confidence'] = result['confidence']
                result['category_enhancement_applied'] = "license_fee_category_mapping"
                logger.debug(f"Set category purpose code to LICF for license fee")
            elif purpose_code == "SUBS":
                result['category_purpose_code'] = "SUBS"
                result['category_confidence'] = result['confidence']
                result['category_enhancement_applied'] = "subscription_category_mapping"
                logger.debug(f"Set category purpose code to SUBS for subscription")
            elif purpose_code == "SCVE":
                result['category_purpose_code'] = "SUPP"
                result['category_confidence'] = result['confidence']
                result['category_enhancement_applied'] = "tech_service_category_mapping"
                logger.debug(f"Set category purpose code to SUPP for tech service")

        # Lower threshold from 0.4 to 0.35 for medium tech relevance
        elif tech_score > 0.35:
            # Medium tech relevance, adjust confidence if prediction is SCVE
            if original_purpose == "SCVE":
                # Boost confidence for SCVE classification
                result['confidence'] = min(original_conf * 1.5, 0.9)
                result['enhancer'] = "tech"
                result['enhanced'] = True
                result['reason'] = "Tech domain boost for SCVE classification"

                # Also enhance category purpose code if it's OTHR or not set
                if result.get('category_purpose_code') in ['OTHR', None, '']:
                    result['category_purpose_code'] = "SUPP"
                    result['category_confidence'] = result['confidence']
                    result['category_enhancement_applied'] = "tech_service_category_mapping"
                    logger.debug(f"Set category purpose code to SUPP for tech service")
            else:
                # Suggest appropriate purpose code as an alternative based on pattern matches
                alternative_purpose = "SCVE"  # Default to SCVE
                alternative_description = "Purchase of Services"

                # Check for specific pattern matches to determine the alternative purpose code
                if "software_license" in matched_keywords:
                    alternative_purpose = "LICF"
                    alternative_description = "License Fee"
                elif "software_development" in matched_keywords or "it_services" in matched_keywords:
                    alternative_purpose = "SCVE"
                    alternative_description = "Purchase of Services"
                elif "platform_infrastructure" in matched_keywords:
                    # Check if it's a subscription or service
                    if re.search(r'\b(subscription|saas|software\s+as\s+a\s+service)\b', narration.lower()):
                        alternative_purpose = "SUBS"
                        alternative_description = "Subscription"
                    else:
                        alternative_purpose = "SCVE"
                        alternative_description = "Purchase of Services"

                result['alternative_purpose'] = alternative_purpose
                result['alternative_description'] = alternative_description
                result['alternative_confidence'] = tech_score
                result['tech_relevance'] = "medium"

        # Add a new lower threshold for weak tech relevance
        elif tech_score > 0.25:
            # Weak tech relevance, just add tech score info without changing classification
            result['tech_relevance'] = "weak"

            # If the original purpose is SCVE, still boost confidence slightly
            if original_purpose == "SCVE":
                result['confidence'] = min(original_conf * 1.2, 0.85)
                result['enhancer'] = "tech"
                result['enhanced'] = True
                result['reason'] = "Minor tech domain boost for SCVE classification"

        return result
