"""
Domain enhancers for the purpose-classifier package.

This module contains specialized enhancers for different domains and transaction types
that improve the accuracy of purpose code classification.
"""

# Basic domain enhancers
from .education_enhancer_semantic import EducationEnhancerSemantic as EducationDomainEnhancer
from .tech_enhancer_semantic import TechDomainEnhancer
from .services_enhancer_semantic import ServicesEnhancerSemantic as ServicesDomainEnhancer
from .trade_enhancer_semantic import TradeEnhancerSemantic as TradeDomainEnhancer
from .transportation_enhancer_semantic import TransportationDomainEnhancer
from .financial_services_enhancer_semantic import FinancialServicesDomainEnhancer
from .category_purpose_enhancer_semantic import CategoryPurposeEnhancerSemantic as CategoryPurposeDomainEnhancer

# Transaction type enhancers
from .tax_enhancer_semantic import TaxEnhancerSemantic as TaxEnhancer
from .card_payment_enhancer_semantic import CardPaymentEnhancerSemantic as CardPaymentEnhancer
from .treasury_enhancer_semantic import TreasuryEnhancerSemantic as TreasuryEnhancer
from .cover_payment_enhancer_semantic import CoverPaymentEnhancerSemantic as CoverPaymentEnhancer
from .court_payment_enhancer_semantic import CourtPaymentEnhancerSemantic as CourtPaymentEnhancer
from .cross_border_enhancer_semantic import CrossBorderEnhancerSemantic as CrossBorderEnhancer

# Additional specialized enhancers
from .dividend_enhancer import DividendEnhancer
from .loan_enhancer import LoanEnhancer
from .pattern_enhancer_semantic import PatternEnhancerSemantic as PatternEnhancer
from .property_purchase_enhancer_semantic import PropertyPurchaseEnhancerSemantic as PropertyPurchaseEnhancer
from .software_services_enhancer_semantic import SoftwareServicesEnhancer
from .message_type_enhancer_semantic import MessageTypeEnhancerSemantic as MessageTypeEnhancer
from .mt103_enhancer import MT103Enhancer
from .salary_enhancer_semantic import SalaryEnhancerSemantic as SalaryEnhancer
from .securities_enhancer_semantic import SecuritiesEnhancerSemantic as SecuritiesEnhancer
from .interbank_enhancer_semantic import InterbankEnhancerSemantic as InterbankEnhancer
from .goods_enhancer_semantic import GoodsEnhancerSemantic as GoodsDomainEnhancer
from .insurance_enhancer_semantic import InsuranceEnhancerSemantic as InsuranceDomainEnhancer
from .forex_enhancer_semantic import ForexEnhancerSemantic as ForexEnhancer
from .trade_settlement_enhancer_semantic import TradeSettlementEnhancerSemantic as TradeSettlementEnhancer
from .government_payment_enhancer_semantic import GovernmentPaymentEnhancerSemantic as GovernmentPaymentEnhancer
from .investment_enhancer_semantic import InvestmentEnhancerSemantic as InvestmentEnhancer
from .travel_enhancer_semantic import TravelEnhancerSemantic as TravelEnhancer
from .rare_codes_enhancer_semantic import RareCodesEnhancer
from .targeted_enhancer_semantic import TargetedEnhancer

# Manager classes
from .enhancer_manager import EnhancerManager
from .enhanced_manager import EnhancedManager
from .adaptive_confidence import AdaptiveConfidenceCalibrator

__all__ = [
    # Basic domain enhancers
    "EducationDomainEnhancer",
    "TechDomainEnhancer",
    "ServicesDomainEnhancer",
    "TradeDomainEnhancer",
    "TransportationDomainEnhancer",
    "FinancialServicesDomainEnhancer",
    "CategoryPurposeDomainEnhancer",

    # Transaction type enhancers
    "TaxEnhancer",
    "CardPaymentEnhancer",
    "TreasuryEnhancer",
    "CoverPaymentEnhancer",
    "CourtPaymentEnhancer",
    "CrossBorderEnhancer",

    # Additional specialized enhancers
    "DividendEnhancer",
    "LoanEnhancer",
    "PatternEnhancer",
    "PropertyPurchaseEnhancer",
    "SoftwareServicesEnhancer",
    "MessageTypeEnhancer",
    "MT103Enhancer",
    "SalaryEnhancer",
    "SecuritiesEnhancer",
    "InterbankEnhancer",
    "GoodsDomainEnhancer",
    "InsuranceDomainEnhancer",
    "ForexEnhancer",
    "TradeSettlementEnhancer",
    "GovernmentPaymentEnhancer",
    "InvestmentEnhancer",
    "TravelEnhancer",
    "RareCodesEnhancer",
    "TargetedEnhancer",

    # Manager classes
    "EnhancerManager",
    "EnhancedManager",
    "AdaptiveConfidenceCalibrator"
]