"""
SoftwareServicesEnhancer for Purpose Code Classifier

This enhancer specializes in identifying software and services-related payments
and improving classification accuracy for these types of transactions.
Uses advanced pattern matching with regular expressions and semantic understanding.
"""

import re
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
import logging

logger = logging.getLogger(__name__)

class SoftwareServicesEnhancer(SemanticEnhancer):
    """
    Enhances classification for software and services-related narrations.
    Uses pattern matching with regular expressions and semantic understanding
    for different types of narrations.
    """

    def __init__(self, matcher=None):
        super().__init__(matcher=matcher)
        self._initialize_patterns()

        # Initialize basic patterns
        self.software_pattern = re.compile(r'\b(software|application|app|program|license|subscription)\b', re.IGNORECASE)
        self.marketing_pattern = re.compile(r'\b(marketing|advertising|promotion|campaign|branding)\b', re.IGNORECASE)
        self.website_pattern = re.compile(r'\b(website|web\s+site|web\s+page|hosting|domain)\b', re.IGNORECASE)
        self.rd_pattern = re.compile(r'\b(research|development|r&d|innovation|prototype)\b', re.IGNORECASE)

    def _initialize_patterns(self):
        """Initialize semantic patterns and contexts."""
        # Direct keywords with purpose codes
        self.direct_keywords = {
            'SOFTWARE': ["software", "subscription", "digital product", "renewal"],
            'MARKETING': ["marketing", "market research", "social media", "email marketing"],
            'WEBSITE': ["website", "webmaster", "domain registration"],
            'RD': ["research", "testing", "research and development"],
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
                'purpose_code': 'SCVE',
                'keywords': ['scve'],
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
                'keywords': ['othr'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['software', 'application', 'app', 'program', 'license', 'subscription', 'renewal', 'activation', 'key', 'code'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['license', 'subscription', 'renewal', 'activation', 'key', 'code', 'software', 'application', 'app', 'program'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['pay', 'ing', 'ment', 'transfer', 'ing', 'for', 'software', 'application', 'app', 'program'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['saas', 'cloud', 'service', 'platform', 'api', 'subscription', 'fee', 'payment', 'invoice'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['digital', 'product', 'download', 'installation', 'upgrade', 'software', 'application', 'app', 'program'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['marketing', 'advertising', 'promotion', 'campaign', 'branding', 'service', 'expense', 'cost', 'fee', 'invoice', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'expense', 'cost', 'fee', 'invoice', 'payment', 'marketing', 'advertising', 'promotion', 'campaign', 'branding'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['pay', 'ing', 'ment', 'transfer', 'ing', 'for', 'marketing', 'advertising', 'promotion', 'campaign', 'branding'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['market', 'research', 'public', 'relations', 'media', 'seo', 'service', 'expense', 'cost', 'fee', 'invoice', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['social', 'media', 'digital', 'marketing', 'content', 'marketing', 'email', 'marketing', 'service', 'expense', 'cost', 'fee', 'invoice', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['marketing', 'expenses', 'marketing', 'costs'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['website', 'web', 'site', 'web', 'page', 'hosting', 'domain', 'design', 'development', 'maintenance', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['hosting', 'domain', 'design', 'development', 'maintenance', 'service', 'website', 'web', 'site', 'web', 'page'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['pay', 'ing', 'ment', 'transfer', 'ing', 'for', 'website', 'web', 'site', 'web', 'page'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['webmaster', 'web', 'service', 'site', 'maintenance', 'web', 'hosting', 'fee', 'payment', 'invoice', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['domain', 'registration', 'dns', 'ssl', 'certificate', 'web', 'server', 'fee', 'payment', 'invoice', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['research', 'development', 'r&d', 'innovation', 'prototype', 'service', 'expense', 'cost', 'fee', 'invoice', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['service', 'expense', 'cost', 'fee', 'invoice', 'payment', 'research', 'development', 'r&d', 'innovation', 'prototype'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['pay', 'ing', 'ment', 'transfer', 'ing', 'for', 'research', 'development', 'r&d', 'innovation', 'prototype'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['testing', 'experiment', 'lab', 'laboratory', 'scientific', 'service', 'expense', 'cost', 'fee', 'invoice', 'payment'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['research', 'and', 'development', 'and', 'development', 'costs'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'keywords': ['software', 'license', 'subscription', 'service'],
                'proximity': 5,
                'weight': 0.8
            },
            {
                'purpose_code': 'OTHR',
                'keywords': ['software', 'license', 'subscription'],
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
        self.semantic_terms = [
            {
                'purpose_code': 'SCVE',
                'term': 'service',
                'threshold': 0.7,
                'weight': 1.0
            },
            {
                'purpose_code': 'SCVE',
                'term': 'consulting',
                'threshold': 0.7,
                'weight': 1.0
            },
            {
                'purpose_code': 'SCVE',
                'term': 'professional',
                'threshold': 0.7,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'term': 'maintenance',
                'threshold': 0.7,
                'weight': 0.9
            },
            {
                'purpose_code': 'SCVE',
                'term': 'repair',
                'threshold': 0.7,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'term': 'installation',
                'threshold': 0.7,
                'weight': 0.8
            },
            {
                'purpose_code': 'SCVE',
                'term': 'support',
                'threshold': 0.7,
                'weight': 0.8
            },
        ]

    def enhance(self, purpose_code, confidence, narration, message_type=None):
        """
        Enhance the purpose code classification for software and services-related narrations.
        Uses advanced pattern matching with regular expressions and semantic understanding.

        Args:
            purpose_code: The predicted purpose code
            confidence: The confidence score of the prediction
            narration: The narration text
            message_type: Optional SWIFT message type (MT103, MT202, etc.)

        Returns:
            tuple: (enhanced_purpose_code, enhanced_confidence, enhancement_type)
        """
        # Skip enhancement if confidence is extremely high
        if confidence > 0.95:
            return purpose_code, confidence, None

        # Convert narration to lowercase for case-insensitive matching
        narration_lower = narration.lower()

        # Advanced pattern matching for software-related narrations
        # These patterns look for semantic relationships between words

        # Software license patterns
        software_license_patterns = [
            r'\b(software|application|app|program)\b.*?\b(license|subscription|renewal|activation|key|code)\b',
            r'\b(license|subscription|renewal|activation|key|code)\b.*?\b(software|application|app|program)\b',
            r'\b(pay(ing|ment)?|transfer(ing)?)\b.*?\b(for|to)\b.*?\b(software|application|app|program)\b',
            r'\b(saas|cloud\s+service|platform|api)\b.*?\b(subscription|fee|payment|invoice)\b',
            r'\b(digital\s+product|download|installation|upgrade)\b.*?\b(software|application|app|program)\b'
        ]

        for pattern in software_license_patterns:
            if re.search(pattern, narration_lower):
                logger.debug(f"Software license pattern matched in narration: {narration}")
                return 'TRAD', 0.99, "software_license"  # Software licenses are considered trade

        # Marketing services patterns
        marketing_services_patterns = [
            r'\b(marketing|advertising|promotion|campaign|branding)\b.*?\b(service|expense|cost|fee|invoice|payment)\b',
            r'\b(service|expense|cost|fee|invoice|payment)\b.*?\b(marketing|advertising|promotion|campaign|branding)\b',
            r'\b(pay(ing|ment)?|transfer(ing)?)\b.*?\b(for|to)\b.*?\b(marketing|advertising|promotion|campaign|branding)\b',
            r'\b(market\s+research|public\s+relations|pr|media|seo)\b.*?\b(service|expense|cost|fee|invoice|payment)\b',
            r'\b(social\s+media|digital\s+marketing|content\s+marketing|email\s+marketing)\b.*?\b(service|expense|cost|fee|invoice|payment)\b'
        ]

        for pattern in marketing_services_patterns:
            if re.search(pattern, narration_lower):
                logger.debug(f"Marketing services pattern matched in narration: {narration}")
                # Special case for "marketing expenses" which should always be SCVE
                if re.search(r'\b(marketing\s+expenses|marketing\s+costs)\b', narration_lower):
                    return 'SCVE', 0.99, "marketing_expenses"  # Marketing expenses are definitely a service
                return 'SCVE', 0.95, "marketing_services"  # Marketing is considered a service

        # Website services patterns
        website_services_patterns = [
            r'\b(website|web\s+site|web\s+page)\b.*?\b(hosting|domain|design|development|maintenance|service)\b',
            r'\b(hosting|domain|design|development|maintenance|service)\b.*?\b(website|web\s+site|web\s+page)\b',
            r'\b(pay(ing|ment)?|transfer(ing)?)\b.*?\b(for|to)\b.*?\b(website|web\s+site|web\s+page)\b',
            r'\b(webmaster|web\s+service|site\s+maintenance|web\s+hosting)\b.*?\b(fee|payment|invoice|service)\b',
            r'\b(domain\s+registration|dns|ssl\s+certificate|web\s+server)\b.*?\b(fee|payment|invoice|service)\b'
        ]

        for pattern in website_services_patterns:
            if re.search(pattern, narration_lower):
                logger.debug(f"Website services pattern matched in narration: {narration}")
                return 'SCVE', 0.95, "website_services"  # Website hosting is considered a service

        # Research and development patterns
        rd_patterns = [
            r'\b(research|development|r&d|innovation|prototype)\b.*?\b(service|expense|cost|fee|invoice|payment)\b',
            r'\b(service|expense|cost|fee|invoice|payment)\b.*?\b(research|development|r&d|innovation|prototype)\b',
            r'\b(pay(ing|ment)?|transfer(ing)?)\b.*?\b(for|to)\b.*?\b(research|development|r&d|innovation|prototype)\b',
            r'\b(testing|experiment|lab|laboratory|scientific)\b.*?\b(service|expense|cost|fee|invoice|payment)\b',
            r'\b(research\s+and\s+development|r\s*&\s*d|r\s+and\s+d|development\s+costs)\b'
        ]

        for pattern in rd_patterns:
            if re.search(pattern, narration_lower):
                logger.debug(f"R&D pattern matched in narration: {narration}")
                return 'SCVE', 0.95, "rd_services"  # R&D is considered a service

        # Message type specific patterns
        if message_type == "MT103":
            # MT103 is commonly used for software and service payments
            if re.search(r'\b(software|license|subscription|service)\b', narration_lower):
                if re.search(r'\b(software|license|subscription)\b', narration_lower):
                    logger.debug(f"MT103 software boost applied in narration: {narration}")
                    return 'TRAD', 0.99, "mt103_software_boost"
                else:
                    logger.debug(f"MT103 service boost applied in narration: {narration}")
                    return 'SCVE', 0.90, "mt103_service_boost"

        # Basic pattern matching as fallback
        if self.software_pattern.search(narration):
            logger.debug(f"Software pattern matched in narration: {narration}")
            return 'TRAD', 0.99, "software_keyword"  # Software is considered trade

        if self.marketing_pattern.search(narration):
            logger.debug(f"Marketing pattern matched in narration: {narration}")
            # Special case for "marketing expenses" which should always be SCVE
            if 'marketing expenses' in narration_lower or 'marketing costs' in narration_lower:
                return 'SCVE', 0.99, "marketing_expenses_keyword"  # Marketing expenses are definitely a service
            return 'SCVE', 0.95, "marketing_keyword"  # Marketing is considered a service

        if self.website_pattern.search(narration):
            logger.debug(f"Website pattern matched in narration: {narration}")
            return 'SCVE', 0.95, "website_keyword"  # Website hosting is considered a service

        if self.rd_pattern.search(narration):
            logger.debug(f"R&D pattern matched in narration: {narration}")
            return 'SCVE', 0.95, "rd_keyword"  # R&D is considered a service

        # Return original prediction if no enhancement applied
        return purpose_code, confidence, None

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance the classification result for software and services-related narrations.
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

        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        enhanced_purpose_code, enhanced_confidence, enhancement_type = self.enhance(purpose_code, confidence, narration, message_type)

        if enhanced_purpose_code != purpose_code:
            result['purpose_code'] = enhanced_purpose_code
            result['confidence'] = enhanced_confidence
            result['enhanced'] = True
            result['enhancement_applied'] = "software_services"
            result['enhancement_type'] = enhancement_type
            result['reason'] = f"Software/services match: {enhancement_type}"

            # Also enhance category purpose code mapping
            if enhanced_purpose_code == 'TRAD':
                # Software is considered trade
                if enhancement_type in ["software_license", "software_keyword", "mt103_software_boost"]:
                    result['category_purpose_code'] = 'TRAD'
                    result['category_confidence'] = 0.95
                    result['category_enhancement_applied'] = "software_category_mapping"
                    logger.debug(f"Set category purpose code to TRAD for software")
            elif enhanced_purpose_code == 'SCVE':
                # Different types of services have different category purpose codes
                if enhancement_type in ["marketing_services", "marketing_expenses", "marketing_keyword", "marketing_expenses_keyword"]:
                    result['category_purpose_code'] = 'SCVE'
                    result['category_confidence'] = 0.95
                    result['category_enhancement_applied'] = "marketing_category_mapping"
                    logger.debug(f"Set category purpose code to SCVE for marketing services")
                elif enhancement_type in ["website_services", "website_keyword"]:
                    result['category_purpose_code'] = 'FCOL'
                    result['category_confidence'] = 0.95
                    result['category_enhancement_applied'] = "website_category_mapping"
                    logger.debug(f"Set category purpose code to FCOL for website services")
                elif enhancement_type in ["rd_services", "rd_keyword"]:
                    result['category_purpose_code'] = 'SUPP'
                    result['category_confidence'] = 0.95
                    result['category_enhancement_applied'] = "rd_category_mapping"
                    logger.debug(f"Set category purpose code to SUPP for R&D services")
                elif enhancement_type == "mt103_service_boost":
                    result['category_purpose_code'] = 'SUPP'
                    result['category_confidence'] = 0.90
                    result['category_enhancement_applied'] = "service_category_mapping"
                    logger.debug(f"Set category purpose code to SUPP for general services")
                else:
                    result['category_purpose_code'] = 'SCVE'
                    result['category_confidence'] = 0.95
                    result['category_enhancement_applied'] = "service_category_mapping"
                    logger.debug(f"Set category purpose code to SCVE for general services")

        return result
