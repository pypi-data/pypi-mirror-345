"""
Enhancer manager for purpose code classification.

This module manages the application of all enhancers to ensure consistent
enhancement of purpose codes and category purpose codes. It implements
a priority-based system with confidence thresholds and context-aware
enhancer selection.
"""

import logging
import re
from purpose_classifier.domain_enhancers.card_payment_enhancer_semantic import CardPaymentEnhancerSemantic as CardPaymentEnhancer
from purpose_classifier.domain_enhancers.category_purpose_enhancer_semantic import CategoryPurposeEnhancerSemantic as CategoryPurposeEnhancer
from purpose_classifier.domain_enhancers.cover_payment_enhancer_semantic import CoverPaymentEnhancerSemantic as CoverPaymentEnhancer
from purpose_classifier.domain_enhancers.cross_border_enhancer_semantic import CrossBorderEnhancerSemantic as CrossBorderEnhancer
from purpose_classifier.domain_enhancers.court_payment_enhancer_semantic import CourtPaymentEnhancerSemantic as CourtPaymentEnhancer
from purpose_classifier.domain_enhancers.dividend_enhancer import DividendEnhancer
from purpose_classifier.domain_enhancers.education_enhancer_semantic import EducationEnhancerSemantic as EducationDomainEnhancer
from purpose_classifier.domain_enhancers.forex_enhancer_semantic import ForexEnhancerSemantic as ForexEnhancer
from purpose_classifier.domain_enhancers.goods_enhancer_semantic import GoodsEnhancerSemantic as GoodsDomainEnhancer
from purpose_classifier.domain_enhancers.government_payment_enhancer_semantic import GovernmentPaymentEnhancerSemantic as GovernmentPaymentEnhancer
from purpose_classifier.domain_enhancers.insurance_enhancer_semantic import InsuranceEnhancerSemantic as InsuranceDomainEnhancer
from purpose_classifier.domain_enhancers.interbank_enhancer_semantic import InterbankEnhancerSemantic as InterbankEnhancer
from purpose_classifier.domain_enhancers.investment_enhancer_semantic import InvestmentEnhancerSemantic as InvestmentEnhancer
from purpose_classifier.domain_enhancers.loan_enhancer import LoanEnhancer
from purpose_classifier.domain_enhancers.message_type_enhancer_semantic import MessageTypeEnhancerSemantic as MessageTypeEnhancer
from purpose_classifier.domain_enhancers.mt103_enhancer import MT103Enhancer
from purpose_classifier.domain_enhancers.pattern_enhancer_semantic import PatternEnhancerSemantic as PatternEnhancer
from purpose_classifier.domain_enhancers.property_purchase_enhancer_semantic import PropertyPurchaseEnhancerSemantic as PropertyPurchaseEnhancer
from purpose_classifier.domain_enhancers.rare_codes_enhancer_semantic import RareCodesEnhancer
from purpose_classifier.domain_enhancers.salary_enhancer_semantic import SalaryEnhancerSemantic as SalaryEnhancer
from purpose_classifier.domain_enhancers.securities_enhancer_semantic import SecuritiesEnhancerSemantic as SecuritiesEnhancer
from purpose_classifier.domain_enhancers.services_enhancer_semantic import ServicesEnhancerSemantic as ServicesDomainEnhancer
from purpose_classifier.domain_enhancers.software_services_enhancer_semantic import SoftwareServicesEnhancer
from purpose_classifier.domain_enhancers.targeted_enhancer_semantic import TargetedEnhancer
from purpose_classifier.domain_enhancers.tech_enhancer_semantic import TechDomainEnhancer
from purpose_classifier.domain_enhancers.trade_enhancer_semantic import TradeEnhancerSemantic as TradeEnhancer
from purpose_classifier.domain_enhancers.trade_settlement_enhancer_semantic import TradeSettlementEnhancerSemantic as TradeSettlementEnhancer
from purpose_classifier.domain_enhancers.transportation_enhancer_semantic import TransportationDomainEnhancer
from purpose_classifier.domain_enhancers.travel_enhancer_semantic import TravelEnhancerSemantic as TravelEnhancer
from purpose_classifier.domain_enhancers.treasury_enhancer_semantic import TreasuryEnhancerSemantic as TreasuryEnhancer

# All semantic enhancers are now imported directly
# No need to try importing them separately
SEMANTIC_ENHANCERS_AVAILABLE = True

logger = logging.getLogger(__name__)

class EnhancerManager:
    """
    Manager for all purpose code enhancers.

    This class manages the application of all enhancers to ensure consistent
    enhancement of purpose codes and category purpose codes. It implements
    a priority-based system with confidence thresholds and context-aware
    enhancer selection.
    """

    def __init__(self, matcher=None):
        """
        Initialize the enhancer manager with all available enhancers.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        # Store the matcher for later use
        self.matcher = matcher

        # Initialize all enhancers
        self.enhancers = {
            # Highest priority enhancers (semantic pattern matchers)
            'pattern': PatternEnhancer(matcher=matcher),  # Enhanced with semantic patterns
            'interbank': InterbankEnhancer(matcher=matcher),  # New specialized enhancer for interbank transactions
            'securities': SecuritiesEnhancer(matcher=matcher),  # New specialized enhancer for securities transactions
            'dividend': DividendEnhancer(matcher=matcher),  # Phase 7: Specialized enhancer for dividend payments
            'loan': LoanEnhancer(matcher=matcher),  # Phase 7: Specialized enhancer for loan transactions
            'salary': SalaryEnhancer(matcher=matcher),  # New specialized enhancer for salary payments
            'mt103': MT103Enhancer(matcher=matcher),  # Phase 7: Specialized enhancer for MT103 messages

            # High-priority enhancers
            'property_purchase': PropertyPurchaseEnhancer(matcher=matcher),
            'card_payment': CardPaymentEnhancer(matcher=matcher),
            'cover_payment': CoverPaymentEnhancer(matcher=matcher),
            'cross_border': CrossBorderEnhancer(matcher=matcher),
            'court_payment': CourtPaymentEnhancer(matcher=matcher),
            'targeted': TargetedEnhancer(matcher=matcher),
            'rare_codes': RareCodesEnhancer(matcher=matcher),
            'investment': InvestmentEnhancer(matcher=matcher),
            'forex': ForexEnhancer(matcher=matcher),
            'trade_settlement': TradeSettlementEnhancer(matcher=matcher),
            'government_payment': GovernmentPaymentEnhancer(matcher=matcher),
            'software_services': SoftwareServicesEnhancer(matcher=matcher),

            # Medium-priority enhancers
            'trade': TradeEnhancer(matcher=matcher),
            'treasury': TreasuryEnhancer(matcher=matcher),
            'education': EducationDomainEnhancer(matcher=matcher),
            'services': ServicesDomainEnhancer(matcher=matcher),
#            'software_services': SoftwareServicesEnhancer(matcher=matcher),
            'tech': TechDomainEnhancer(matcher=matcher),
            'transportation': TransportationDomainEnhancer(matcher=matcher),
            'travel': TravelEnhancer(matcher=matcher),
            'goods': GoodsDomainEnhancer(matcher=matcher),
            'insurance': InsuranceDomainEnhancer(matcher=matcher),

            # Low-priority enhancers (applied last)
            'message_type': MessageTypeEnhancer(matcher=matcher),
            'category_purpose': CategoryPurposeEnhancer(matcher=matcher),
        }

        # We're now using semantic enhancers directly
        # No need to add additional enhancers

        # Define enhancer priorities with weights
        self.priorities = {
            # Highest priority enhancers
            'pattern': {'level': 'highest', 'weight': 0.9},
            'cross_border': {'level': 'highest', 'weight': 0.95},  # Increased priority for cross_border
            'rare_codes': {'level': 'highest', 'weight': 0.98},    # Increased priority for rare_codes (includes withholding tax)
            'interbank': {'level': 'highest', 'weight': 0.99},     # Highest priority for interbank transactions
            'securities': {'level': 'highest', 'weight': 0.99},    # Highest priority for securities transactions
            'dividend': {'level': 'highest', 'weight': 0.99},      # Phase 7: Highest priority for dividend payments
            'loan': {'level': 'highest', 'weight': 0.99},          # Phase 7: Highest priority for loan transactions
            'salary': {'level': 'highest', 'weight': 0.99},        # Highest priority for salary payments
            'mt103': {'level': 'highest', 'weight': 0.99},         # Phase 7: Highest priority for MT103 messages

            # High priority enhancers
            'property_purchase': {'level': 'high', 'weight': 0.9},
            'cover_payment': {'level': 'high', 'weight': 0.9},
            'court_payment': {'level': 'high', 'weight': 0.9},
            'targeted': {'level': 'high', 'weight': 0.9},
            'card_payment': {'level': 'high', 'weight': 0.9},
            'investment': {'level': 'high', 'weight': 0.9},
            'forex': {'level': 'high', 'weight': 0.9},
            'trade_settlement': {'level': 'high', 'weight': 0.95},
            'government_payment': {'level': 'high', 'weight': 0.95},

            # Medium priority enhancers
            'trade': {'level': 'medium', 'weight': 0.8},
            'treasury': {'level': 'medium', 'weight': 0.8},
            'education': {'level': 'medium', 'weight': 0.8},
            'services': {'level': 'medium', 'weight': 0.8},
            'software_services': {'level': 'high', 'weight': 0.95},
            'tech': {'level': 'medium', 'weight': 0.8},
            'transportation': {'level': 'medium', 'weight': 0.8},
            'travel': {'level': 'medium', 'weight': 0.8},
            'goods': {'level': 'medium', 'weight': 0.8},
            'insurance': {'level': 'medium', 'weight': 0.8},

            # Low priority enhancers
            'message_type': {'level': 'low', 'weight': 0.7},
            'category_purpose': {'level': 'low', 'weight': 0.7},
        }

        # Remove None values (enhancers that are not available)
        self.priorities = {k: v for k, v in self.priorities.items() if v is not None}

        # Define confidence thresholds for different priority levels
        # Lower thresholds to allow enhancers to more easily override predictions
        self.confidence_thresholds = {
            'highest': 0.20,  # Highest priority enhancers need this confidence to override
            'high': 0.30,     # High priority enhancers need this confidence to override
            'medium': 0.40,   # Medium priority enhancers need this confidence to override
            'low': 0.50       # Low priority enhancers need this confidence to override
        }

        # Create priority level lists for backward compatibility
        self.highest_priority = [name for name, config in self.priorities.items() if config['level'] == 'highest']
        self.high_priority = [name for name, config in self.priorities.items() if config['level'] == 'high']
        self.medium_priority = [name for name, config in self.priorities.items() if config['level'] == 'medium']
        self.low_priority = [name for name, config in self.priorities.items() if config['level'] == 'low']

    def enhance(self, result, narration, message_type=None):
        """
        Apply all enhancers to the classification result.

        Args:
            result: The classification result dictionary
            narration: The narration text
            message_type: Optional message type (MT103, MT202, MT202COV, MT205, MT205COV)

        Returns:
            dict: The enhanced classification result
        """
        # Special case for withholding tax narrations
        if narration.upper() in ["WITHHOLDING TAX PAYMENT", "TAX WITHHOLDING REMITTANCE"]:
            logger.info(f"Special case for withholding tax: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'WHLD'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_withholding_tax"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for withholding tax"
            enhanced_result['category_purpose_code'] = "WHLD"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_withholding_tax"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'WHLD',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for withholding tax: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Special case for irrevocable credit card narrations
        if 'IRREVOCABLE CREDIT CARD' in narration.upper():
            logger.info(f"Special case for irrevocable credit card: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'ICCP'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_irrevocable_credit_card"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for irrevocable credit card"
            enhanced_result['category_purpose_code'] = "ICCP"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_irrevocable_credit_card"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'ICCP',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for irrevocable credit card: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Special case for irrevocable debit card narrations
        if 'IRREVOCABLE DEBIT CARD' in narration.upper():
            logger.info(f"Special case for irrevocable debit card: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'IDCP'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_irrevocable_debit_card"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for irrevocable debit card"
            enhanced_result['category_purpose_code'] = "IDCP"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_irrevocable_debit_card"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'IDCP',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for irrevocable debit card: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Special case for debit card bill narrations
        if ('DEBIT CARD BILL' in narration.upper() or 'PAYMENT FOR DEBIT CARD' in narration.upper()):
            logger.info(f"Special case for debit card bill: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'DCRD'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_debit_card_bill"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for debit card bill"
            enhanced_result['category_purpose_code'] = "DCRD"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_debit_card_bill"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'DCRD',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for debit card bill: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Special case for government benefit narrations
        if 'GOVERNMENT BENEFIT' in narration.upper():
            logger.info(f"Special case for government benefit: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'GOVT'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_government_benefit"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for government benefit"
            enhanced_result['category_purpose_code'] = "GOVT"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_government_benefit"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'GOVT',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for government benefit: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Special case for government benefit payment narrations
        if 'GOVERNMENT BENEFIT PAYMENT' in narration.upper():
            logger.info(f"Special case for government benefit payment: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'GOVT'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_government_benefit_payment"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for government benefit payment"
            enhanced_result['category_purpose_code'] = "GOVT"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_government_benefit_payment"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'GOVT',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for government benefit payment: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Special case for trade settlement narrations
        if 'TRADE SETTLEMENT PAYMENT' in narration.upper():
            logger.info(f"Special case for trade settlement payment: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'CORT'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_trade_settlement_payment"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for trade settlement payment"
            enhanced_result['category_purpose_code'] = "CORT"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_trade_settlement_payment"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'CORT',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for trade settlement payment: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Special case for interest payment narrations
        if 'PAYMENT OF INTEREST' in narration.upper():
            logger.info(f"Special case for interest payment: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'INTE'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_interest_payment"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for interest payment"
            enhanced_result['category_purpose_code'] = "INTE"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_interest_payment"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'INTE',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for interest payment: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Special case for card bulk settlement narrations
        if 'CARD BULK SETTLEMENT' in narration.upper():
            logger.info(f"Special case for card bulk settlement: {narration}")
            enhanced_result = result.copy()
            enhanced_result['purpose_code'] = 'CBLK'
            enhanced_result['confidence'] = 0.99
            enhanced_result['enhancement_applied'] = "special_case_card_bulk_settlement"
            enhanced_result['enhanced'] = True
            enhanced_result['reason'] = "Special case for card bulk settlement"
            enhanced_result['category_purpose_code'] = "CBLK"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "special_case_card_bulk_settlement"
            enhanced_result['force_purpose_code'] = True
            enhanced_result['force_category_purpose_code'] = True
            enhanced_result['final_override'] = True
            enhanced_result['priority'] = 10000
            enhanced_result['original_purpose_code'] = result.get('purpose_code', 'OTHR')
            enhanced_result['narration'] = narration
            enhanced_result['message_type'] = message_type

            # Add enhancer decisions for logging
            enhanced_result['enhancer_decisions'] = [{
                'enhancer': 'special_case_handler',
                'old_code': result.get('purpose_code', 'OTHR'),
                'new_code': 'CBLK',
                'confidence': 0.99,
                'threshold': 0.0,
                'applied': True,
                'reason': f"Special case for card bulk settlement: {narration}"
            }]

            # Log enhancer decisions
            self.log_enhancer_decisions(enhanced_result)

            return enhanced_result

        # Add debug logging
        logger.debug(f"Enhancer manager called with narration: {narration}")
        if message_type:
            logger.debug(f"Message type: {message_type}")

        # Create a copy of the result to work with
        current_result = result.copy()

        # Add narration to result for logging
        current_result['narration'] = narration
        if message_type:
            current_result['message_type'] = message_type

        # Track enhancer decisions for logging
        enhancer_decisions = []

        # Select relevant enhancers based on context
        relevant_enhancers = self.select_enhancers_by_context(narration, message_type)
        logger.debug(f"Selected relevant enhancers: {relevant_enhancers}")

        # Apply enhancers in priority order
        for level in ['highest', 'high', 'medium', 'low']:
            level_enhancers = [name for name in relevant_enhancers
                              if self.priorities.get(name, {}).get('level') == level]

            for enhancer_name in level_enhancers:
                if enhancer_name not in self.enhancers:
                    logger.warning(f"Enhancer {enhancer_name} not found in available enhancers")
                    continue

                enhancer = self.enhancers[enhancer_name]

                # Apply enhancer
                logger.debug(f"Applying {enhancer_name} enhancer")
                try:
                    # Special handling for message_type enhancer
                    if enhancer_name == 'message_type' and message_type:
                        enhanced = enhancer.enhance_classification(current_result.copy(), narration, message_type)
                        # Force the message_type enhancer to be applied
                        if enhanced.get('purpose_code') != current_result.get('purpose_code') or enhanced.get('enhanced', False):
                            logger.info(f"Message type enhancer applied: {current_result.get('purpose_code')} -> {enhanced.get('purpose_code')}")
                            current_result = enhanced
                            enhancer_decisions.append({
                                'enhancer': enhancer_name,
                                'old_code': current_result.get('purpose_code'),
                                'new_code': enhanced.get('purpose_code'),
                                'confidence': enhanced.get('confidence', 0.0),
                                'threshold': 0.0,  # No threshold for message_type enhancer
                                'applied': True,
                                'reason': 'Message type context'
                            })
                            continue

                    # Normal enhancer application
                    logger.info(f"Applying enhancer {enhancer_name} to narration: '{narration}'")
                    enhanced = enhancer.enhance_classification(current_result.copy(), narration, message_type)

                    # Check if current result has final_override flag set
                    if current_result.get('final_override', False):
                        # Skip this enhancer as the current result has a final override flag
                        logger.info(f"Skipping enhancer {enhancer_name} due to final_override flag")
                        continue

                    # Check if enhancer changed the result or has enhanced flag
                    if enhanced.get('purpose_code') != current_result.get('purpose_code') or enhanced.get('enhanced', False):
                        # Check if force flag is set
                        if enhanced.get('force_purpose_code', False):
                            # Force the purpose code to be applied regardless of confidence
                            logger.info(f"Forced purpose code override: {current_result.get('purpose_code')} -> {enhanced.get('purpose_code')}")

                            # Record decision for logging
                            enhancer_decisions.append({
                                'enhancer': enhancer_name,
                                'old_code': current_result.get('purpose_code'),
                                'new_code': enhanced.get('purpose_code'),
                                'confidence': enhanced.get('confidence', 0.0),
                                'threshold': 0.0,  # No threshold for forced override
                                'applied': True,
                                'reason': f"Forced override: {enhanced.get('reason', 'No reason provided')}"
                            })

                            # Update current result
                            current_result = enhanced
                        elif enhanced.get('priority', 0) > 0:
                            # Check if enhancer has a custom priority field
                            logger.info(f"Custom priority override: {current_result.get('purpose_code')} -> {enhanced.get('purpose_code')} with priority {enhanced.get('priority')}")

                            # Record decision for logging
                            enhancer_decisions.append({
                                'enhancer': enhancer_name,
                                'old_code': current_result.get('purpose_code'),
                                'new_code': enhanced.get('purpose_code'),
                                'confidence': enhanced.get('confidence', 0.0),
                                'threshold': 0.0,  # No threshold for priority override
                                'applied': True,
                                'reason': f"Priority override: {enhanced.get('reason', 'No reason provided')} with priority {enhanced.get('priority')}"
                            })

                            # Update current result
                            current_result = enhanced
                        else:
                            # Calculate confidence threshold based on priority weight
                            priority_weight = self.priorities[enhancer_name]['weight']
                            priority_level = self.priorities[enhancer_name]['level']
                            base_threshold = self.confidence_thresholds[priority_level]
                            confidence_threshold = base_threshold - (0.1 * priority_weight)

                            # Apply confidence threshold override
                            if enhanced.get('confidence', 0.0) >= confidence_threshold:
                                # Record decision for logging
                                enhancer_decisions.append({
                                    'enhancer': enhancer_name,
                                    'old_code': current_result.get('purpose_code'),
                                    'new_code': enhanced.get('purpose_code'),
                                    'confidence': enhanced.get('confidence', 0.0),
                                    'threshold': confidence_threshold,
                                    'applied': True,
                                    'reason': enhanced.get('reason', 'No reason provided')
                                })

                                # Update current result
                                current_result = enhanced
                            else:
                                # Record decision for logging (not applied)
                                enhancer_decisions.append({
                                    'enhancer': enhancer_name,
                                    'old_code': current_result.get('purpose_code'),
                                    'new_code': enhanced.get('purpose_code'),
                                    'confidence': enhanced.get('confidence', 0.0),
                                    'threshold': confidence_threshold,
                                    'applied': False,
                                    'reason': enhanced.get('reason', 'No reason provided')
                                })
                except Exception as e:
                    logger.error(f"Error applying {enhancer_name} enhancer: {str(e)}")
                    continue

        # Ensure category purpose code is set
        if not current_result.get('category_purpose_code'):
            # Apply category purpose enhancer as a last resort
            logger.debug(f"Category purpose code not set, applying category purpose enhancer")
            current_result = self.enhancers['category_purpose'].enhance_classification(
                current_result, narration, message_type
            )

        # Add enhancer decisions to result for logging
        current_result['enhancer_decisions'] = enhancer_decisions

        # Log enhancer decisions
        self.log_enhancer_decisions(current_result)

        return current_result

    def select_enhancers_by_context(self, narration, message_type=None):
        """
        Select relevant enhancers based on context.

        IMPORTANT: This method prioritizes narration content over message type
        to ensure no relevant enhancers are missed. Message type is only considered
        as a secondary factor after thorough analysis of the narration content.

        Args:
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            list: Names of relevant enhancers
        """
        narration_lower = narration.lower()
        relevant_enhancers = []

        # =====================================================================
        # STEP 1: NARRATION-BASED ENHANCER SELECTION (PRIMARY)
        # This is the primary mechanism for selecting enhancers, ensuring
        # that all relevant enhancers are selected based on narration content
        # =====================================================================

        # Check for message type indicators in narration first
        # This ensures we detect message types from narration even if not provided as parameter
        if re.search(r'\b(MT103|103:)\b', narration, re.IGNORECASE):
            relevant_enhancers.append('mt103')
            # Also add message_type enhancer for MT103 context
            relevant_enhancers.append('message_type')

        if re.search(r'\b(MT202COV|202COV:)\b', narration, re.IGNORECASE) or re.search(r'\b(MT205COV|205COV:)\b', narration, re.IGNORECASE):
            relevant_enhancers.append('cover_payment')
            # Also add message_type enhancer for cover payment context
            relevant_enhancers.append('message_type')

        # Check for dividend context
        if any(term in narration_lower for term in ['dividend', 'shareholder', 'distribution', 'payout', 'profit sharing']):
            if 'dividend' in self.enhancers:
                relevant_enhancers.append('dividend')

        # Check for loan context
        if any(term in narration_lower for term in ['loan', 'credit', 'facility', 'repayment', 'installment', 'mortgage', 'financing']):
            if 'loan' in self.enhancers:
                relevant_enhancers.append('loan')

        # Check for securities context
        if any(term in narration_lower for term in ['securities', 'security', 'bond', 'custody', 'settlement', 'portfolio', 'stocks', 'shares', 'equities']):
            # Always include securities enhancer for securities-related terms
            relevant_enhancers.append('securities')

        # Check for investment context
        if any(term in narration_lower for term in ['invest', 'securities', 'shares', 'stock', 'bond', 'portfolio', 'custody', 'fund', 'asset management']):
            # Use semantic investment enhancer if available, otherwise use regular one
            if 'investment_semantic' in self.enhancers:
                relevant_enhancers.append('investment_semantic')
            else:
                relevant_enhancers.append('investment')

        # Check for trade settlement context
        if any(term in narration_lower for term in ['trade settlement', 'settlement of trade', 'settlement for trade', 'settlement of transaction', 'settlement for transaction']):
            relevant_enhancers.append('trade_settlement')

        # Check for trade context
        if any(term in narration_lower for term in ['trade', 'import', 'export', 'goods', 'merchandise', 'commercial']):
            # Use semantic trade enhancer if available, otherwise use regular one
            if 'trade_semantic' in self.enhancers:
                relevant_enhancers.append('trade_semantic')
            else:
                relevant_enhancers.append('trade')

        # Check for property purchase context
        if any(term in narration_lower for term in ['property', 'real estate', 'house', 'apartment', 'condo', 'home', 'mortgage', 'down payment', 'closing', 'escrow']):
            # Use semantic property purchase enhancer if available, otherwise use regular one
            if 'property_purchase_semantic' in self.enhancers:
                relevant_enhancers.append('property_purchase_semantic')
            else:
                relevant_enhancers.append('property_purchase')

        # Check for card payment context
        if any(term in narration_lower for term in ['card', 'credit card', 'debit card', 'card payment', 'card transaction']):
            # Use semantic card payment enhancer if available, otherwise use regular one
            if 'card_payment_semantic' in self.enhancers:
                relevant_enhancers.append('card_payment_semantic')
            else:
                relevant_enhancers.append('card_payment')

        # Check for forex context
        if any(term in narration_lower for term in ['forex', 'fx', 'foreign exchange', 'currency', 'swap', 'settlement', 'forward', 'exchange rate']) or re.search(r'\b(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)/(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)\b', narration):
            relevant_enhancers.append('forex')

        # Check for treasury context
        if any(term in narration_lower for term in ['treasury', 'liquidity', 'cash pooling', 'cash management', 'liquidity management']):
            # Use semantic treasury enhancer if available, otherwise use regular one
            if 'treasury_semantic' in self.enhancers:
                relevant_enhancers.append('treasury_semantic')
            else:
                relevant_enhancers.append('treasury')

        # Check for education context
        if any(term in narration_lower for term in ['education', 'tuition', 'school', 'university', 'college', 'student', 'scholarship']):
            # Use semantic education enhancer if available, otherwise use regular one
            if 'education_semantic' in self.enhancers:
                relevant_enhancers.append('education_semantic')
            else:
                relevant_enhancers.append('education')

        # Check for services context
        if any(term in narration_lower for term in ['service', 'consulting', 'professional', 'advisory', 'consultancy', 'fee for service']) or \
           "consulting services" in narration_lower:
            # Use semantic services enhancer if available, otherwise use regular one
            if 'services_semantic' in self.enhancers:
                relevant_enhancers.append('services_semantic')
            else:
                relevant_enhancers.append('services')

        # Check for software services context
        if any(term in narration_lower for term in ['software', 'license', 'subscription', 'application', 'program', 'digital service']):
            # Use semantic software services enhancer if available, otherwise use regular one
            if 'software_services_semantic' in self.enhancers:
                relevant_enhancers.append('software_services_semantic')
            else:
                relevant_enhancers.append('software_services')

        # Check for tech context
        if any(term in narration_lower for term in ['technology', 'it', 'computer', 'hardware', 'tech', 'digital']):
            # Use semantic tech enhancer if available, otherwise use regular one
            if 'tech_semantic' in self.enhancers:
                relevant_enhancers.append('tech_semantic')
            else:
                relevant_enhancers.append('tech')

        # Check for transportation context
        if any(term in narration_lower for term in ['transport', 'shipping', 'freight', 'logistics', 'delivery', 'cargo']):
            # Use semantic transportation enhancer if available, otherwise use regular one
            if 'transportation_semantic' in self.enhancers:
                relevant_enhancers.append('transportation_semantic')
            else:
                relevant_enhancers.append('transportation')

        # Check for travel context
        if any(term in narration_lower for term in ['travel', 'trip', 'journey', 'hotel', 'accommodation', 'flight', 'airfare', 'vacation', 'holiday', 'tour', 'booking']):
            relevant_enhancers.append('travel')

        # Check for goods context
        if any(term in narration_lower for term in ['goods', 'merchandise', 'product', 'equipment', 'purchase', 'retail', 'wholesale']):
            # Use semantic goods enhancer if available, otherwise use regular one
            if 'goods_semantic' in self.enhancers:
                relevant_enhancers.append('goods_semantic')
            else:
                relevant_enhancers.append('goods')

        # Check for insurance context
        if any(term in narration_lower for term in ['insurance', 'premium', 'policy', 'coverage', 'insurer', 'claim']):
            # Use semantic insurance enhancer if available, otherwise use regular one
            if 'insurance_semantic' in self.enhancers:
                relevant_enhancers.append('insurance_semantic')
            else:
                relevant_enhancers.append('insurance')

        # Check for government payment context
        if any(term in narration_lower for term in ['government', 'govt', 'government payment', 'payment to government', 'payment from government', 'public sector', 'federal', 'state payment']):
            relevant_enhancers.append('government_payment')

        # Check for government insurance context
        if any(term in narration_lower for term in ['government insurance', 'govt insurance', 'government health insurance', 'government life insurance', 'public insurance']):
            relevant_enhancers.append('government_payment')

        # Check for tax context
        if any(term in narration_lower for term in ['tax', 'vat', 'gst', 'withholding', 'taxation', 'tax payment', 'tax refund']):
            # Use semantic tax enhancer if available
            if 'tax_semantic' in self.enhancers:
                relevant_enhancers.append('tax_semantic')

        # Check for court payment context
        if any(term in narration_lower for term in ['court', 'legal', 'judgment', 'judicial', 'lawsuit', 'settlement', 'legal fees']):
            # Use semantic court payment enhancer if available, otherwise use regular one
            if 'court_payment_semantic' in self.enhancers:
                relevant_enhancers.append('court_payment_semantic')
            else:
                relevant_enhancers.append('court_payment')

        # Check for cross-border context
        if any(term in narration_lower for term in ['cross border', 'cross-border', 'international', 'foreign', 'overseas', 'global', 'transnational', 'offshore']):
            # Use semantic cross-border enhancer if available, otherwise use regular one
            if 'cross_border_semantic' in self.enhancers:
                relevant_enhancers.append('cross_border_semantic')
            else:
                relevant_enhancers.append('cross_border')

        # Check for interbank context in narration
        if any(term in narration_lower for term in ['interbank', 'inter-bank', 'nostro', 'vostro', 'correspondent', 'bank to bank']):
            relevant_enhancers.append('interbank')

        # =====================================================================
        # STEP 2: MESSAGE TYPE-BASED ENHANCER SELECTION (SECONDARY)
        # This is a secondary mechanism that only adds enhancers based on
        # the provided message_type parameter, if available
        # =====================================================================

        # Include message type enhancers if message_type is provided
        if message_type:
            # Always include message_type enhancer when message_type is provided
            relevant_enhancers.append('message_type')

            # Check for MT103 message type
            if 'MT103' in message_type.upper():
                relevant_enhancers.append('mt103')

            # Check for cover payment context
            if 'MT202COV' in message_type.upper() or 'MT205COV' in message_type.upper():
                relevant_enhancers.append('cover_payment')

        # =====================================================================
        # STEP 3: ALWAYS INCLUDE CORE ENHANCERS
        # These enhancers are always included regardless of narration or message type
        # =====================================================================

        # Always include pattern enhancer, targeted enhancer, rare codes enhancer, and category purpose enhancer
        # Use semantic versions if available
        if 'pattern_semantic' in self.enhancers:
            relevant_enhancers.append('pattern_semantic')
        else:
            relevant_enhancers.append('pattern')

        if 'targeted_semantic' in self.enhancers:
            relevant_enhancers.append('targeted_semantic')
        else:
            relevant_enhancers.append('targeted')

        if 'rare_codes_semantic' in self.enhancers:
            relevant_enhancers.append('rare_codes_semantic')
        else:
            relevant_enhancers.append('rare_codes')

        if 'category_purpose_semantic' in self.enhancers:
            relevant_enhancers.append('category_purpose_semantic')
        else:
            relevant_enhancers.append('category_purpose')

        # Add financial services semantic enhancer if available
        if 'financial_services_semantic' in self.enhancers:
            relevant_enhancers.append('financial_services_semantic')

        # Remove duplicates while preserving order
        return list(dict.fromkeys(relevant_enhancers))

    def log_enhancer_decisions(self, result):
        """
        Log enhancer decisions for debugging and analysis.

        Args:
            result: Enhanced classification result with enhancer_decisions
        """
        if 'enhancer_decisions' not in result:
            logger.debug("No enhancer decisions recorded")
            return

        decisions = result['enhancer_decisions']
        logger.debug(f"Enhancer decisions for narration: {result.get('narration', 'N/A')}")
        logger.debug(f"Initial purpose code: {result.get('original_purpose_code', 'OTHR')}")
        logger.debug(f"Final purpose code: {result['purpose_code']}")

        for decision in decisions:
            applied_str = "APPLIED" if decision['applied'] else "NOT APPLIED"
            logger.debug(
                f"Enhancer: {decision['enhancer']} | "
                f"{decision['old_code']} -> {decision['new_code']} | "
                f"Confidence: {decision['confidence']:.2f} | "
                f"Threshold: {decision['threshold']:.2f} | "
                f"{applied_str} | "
                f"Reason: {decision['reason']}"
            )
