"""
Salary enhancer for purpose code classification.

This enhancer focuses on improving the classification of SALA (Salary Payment)
purpose code, which is one of the important codes for MT103 messages.
"""

import re
import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

logger = logging.getLogger(__name__)

class SalaryEnhancerSemantic(SemanticEnhancer):
    """
    Enhancer for salary-related purpose codes.

    This enhancer improves the classification of salary-related purpose codes
    by using advanced pattern matching with regular expressions and semantic understanding.
    """

    def __init__(self, matcher=None):
        """
        Initialize the salary enhancer.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize patterns for salary detection."""
        # Direct keywords with purpose codes
        self.direct_keywords = {
            'SALA': [
                'salary payment', 'salary transfer', 'monthly salary', 'employee salary',
                'staff salary', 'payroll', 'wage payment', 'wage transfer', 'monthly wage',
                'employee wage', 'staff wage', 'compensation payment', 'remuneration',
                'employee compensation', 'staff compensation', 'monthly compensation',
                'salary disbursement', 'wage disbursement', 'payroll disbursement',
                'salary credit', 'wage credit', 'payroll credit', 'employee payment',
                'staff payment', 'monthly payment to employee', 'monthly payment to staff',
                'salary for', 'wages for', 'payroll for', 'compensation for',
                'employee monthly payment', 'staff monthly payment'
            ]
        }

        # Context patterns for salary-related transactions
        self.context_patterns = [
            # Salary patterns
            r'\b(salary|salaries)\b',
            r'\b(wage|wages)\b',
            r'\b(payroll)\b',
            r'\b(compensation)\b',
            r'\b(remuneration)\b',
            r'\b(employee|staff)\s+(payment|transfer|credit)\b',
            r'\b(payment|transfer|credit)\s+to\s+(employee|staff)\b',
            r'\b(monthly)\s+(payment|transfer|credit)\s+to\s+(employee|staff)\b',
            r'\b(monthly)\s+(employee|staff)\s+(payment|transfer|credit)\b',
            r'\b(employee|staff)\s+(monthly)\s+(payment|transfer|credit)\b',
            r'\b(salary|wage|payroll|compensation)\s+for\s+(month|period|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(salary|wage|payroll|compensation)\b',
            r'\b(salary|wage|payroll|compensation)\s+\d{4}\b',  # Salary 2023
            r'\b(salary|wage|payroll|compensation)\s+\d{1,2}/\d{4}\b',  # Salary 05/2023
            r'\b(salary|wage|payroll|compensation)\s+\d{1,2}-\d{4}\b',  # Salary 05-2023
            r'\b(net)\s+(salary|wage|payroll|compensation)\b',
            r'\b(gross)\s+(salary|wage|payroll|compensation)\b',
            r'\b(salary|wage|payroll|compensation)\s+(payment|transfer|credit|deposit)\b',
            r'\b(payment|transfer|credit|deposit)\s+of\s+(salary|wage|payroll|compensation)\b',
            r'\b(employee|staff)\s+(monthly)\s+(income|earnings)\b',
            r'\b(monthly)\s+(income|earnings)\s+for\s+(employee|staff)\b',
            r'\b(salary|wage|payroll|compensation)\s+transfer\b',
            r'\b(transfer)\s+of\s+(salary|wage|payroll|compensation)\b',
            r'\b(employee|staff)\s+(benefit|benefits)\b',
            r'\b(employee|staff)\s+(payment|transfer|credit)\s+for\s+(month|period|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
            r'\b(monthly)\s+(employee|staff)\s+(payment|transfer|credit)\s+for\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
            r'\b(salary|wage|payroll|compensation)\s+for\s+(employee|staff)\b',
            r'\b(employee|staff)\s+(salary|wage|payroll|compensation)\s+for\s+(month|period|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
            r'\b(employee|staff)\s+(salary|wage|payroll|compensation)\s+for\s+\d{4}\b',  # Employee salary for 2023
            r'\b(employee|staff)\s+(salary|wage|payroll|compensation)\s+for\s+\d{1,2}/\d{4}\b',  # Employee salary for 05/2023
            r'\b(employee|staff)\s+(salary|wage|payroll|compensation)\s+for\s+\d{1,2}-\d{4}\b',  # Employee salary for 05-2023
        ]

        # Semantic terms for salary-related transactions
        self.semantic_terms = [
            'salary', 'wage', 'payroll', 'compensation', 'remuneration',
            'employee payment', 'staff payment', 'monthly payment',
            'employee transfer', 'staff transfer', 'monthly transfer',
            'employee credit', 'staff credit', 'monthly credit',
            'employee deposit', 'staff deposit', 'monthly deposit',
            'employee earnings', 'staff earnings', 'monthly earnings',
            'employee income', 'staff income', 'monthly income',
            'employee benefit', 'staff benefit', 'monthly benefit',
            'employee salary', 'staff salary', 'monthly salary',
            'employee wage', 'staff wage', 'monthly wage',
            'employee payroll', 'staff payroll', 'monthly payroll',
            'employee compensation', 'staff compensation', 'monthly compensation',
            'employee remuneration', 'staff remuneration', 'monthly remuneration',
            'salary payment', 'wage payment', 'payroll payment', 'compensation payment',
            'salary transfer', 'wage transfer', 'payroll transfer', 'compensation transfer',
            'salary credit', 'wage credit', 'payroll credit', 'compensation credit',
            'salary deposit', 'wage deposit', 'payroll deposit', 'compensation deposit',
            'salary for month', 'wage for month', 'payroll for month', 'compensation for month',
            'salary for period', 'wage for period', 'payroll for period', 'compensation for period',
            'net salary', 'gross salary', 'net wage', 'gross wage',
            'net payroll', 'gross payroll', 'net compensation', 'gross compensation',
            'salary disbursement', 'wage disbursement', 'payroll disbursement', 'compensation disbursement',
            'monthly salary payment', 'monthly wage payment', 'monthly payroll payment', 'monthly compensation payment',
            'monthly salary transfer', 'monthly wage transfer', 'monthly payroll transfer', 'monthly compensation transfer',
            'monthly salary credit', 'monthly wage credit', 'monthly payroll credit', 'monthly compensation credit',
            'monthly salary deposit', 'monthly wage deposit', 'monthly payroll deposit', 'monthly compensation deposit',
            'monthly employee payment', 'monthly staff payment', 'monthly employee transfer', 'monthly staff transfer',
            'monthly employee credit', 'monthly staff credit', 'monthly employee deposit', 'monthly staff deposit',
            'payment to employee', 'payment to staff', 'transfer to employee', 'transfer to staff',
            'credit to employee', 'credit to staff', 'deposit to employee', 'deposit to staff',
            'payment for employee', 'payment for staff', 'transfer for employee', 'transfer for staff',
            'credit for employee', 'credit for staff', 'deposit for employee', 'deposit for staff',
            'employee monthly payment', 'staff monthly payment', 'employee monthly transfer', 'staff monthly transfer',
            'employee monthly credit', 'staff monthly credit', 'employee monthly deposit', 'staff monthly deposit',
        ]

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for salary-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        logger.debug(f"Salary enhancer called with narration: {narration}")

        # Get current purpose code and confidence
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Don't override high confidence classifications
        if confidence >= 0.95 and purpose_code != 'CCRD':
            logger.debug(f"Not overriding high confidence classification: {purpose_code} ({confidence})")
            return result

        # Special case for CCRD misclassification
        if purpose_code == 'CCRD' and confidence >= 0.7:
            # Check if this is actually a salary payment
            narration_lower = narration.lower()
            if any(term in narration_lower for term in ['salary', 'wage', 'payroll', 'employee', 'staff', 'compensation']):
                logger.info(f"Correcting CCRD misclassification to SALA for salary-related narration: {narration}")
                return self._create_enhanced_result(result, 'SALA', 0.99, "Correcting CCRD misclassification for salary")

        # Call the base implementation first
        enhanced_result = super().enhance_classification(result, narration, message_type)

        # If the base implementation changed something, return it
        if enhanced_result != result:
            # Ensure category purpose code is set to SALA for salary
            if enhanced_result.get('purpose_code') == "SALA":
                enhanced_result['category_purpose_code'] = "SALA"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "salary_category_mapping"
            return enhanced_result

        # Check if we should override the current classification
        if self.should_override_classification(result, narration):
            logger.info(f"Overriding {purpose_code} with SALA based on context analysis")
            enhanced_result = self._create_enhanced_result(result, 'SALA', 0.95, "Context analysis override")

            # Ensure category purpose code is set to SALA for salary
            enhanced_result['category_purpose_code'] = "SALA"
            enhanced_result['category_confidence'] = 0.99
            enhanced_result['category_enhancement_applied'] = "salary_category_mapping"

            return enhanced_result

        # Message type specific considerations
        if message_type == "MT103":
            # MT103 is commonly used for salary payments
            # Enhanced pattern matching for MT103 salary payments
            narration_lower = narration.lower()
            
            # Check for employee/staff/salary terms
            employee_terms = ['employee', 'staff', 'personnel', 'worker', 'workforce']
            salary_terms = ['salary', 'wage', 'payroll', 'compensation', 'remuneration', 'payment', 'transfer']
            
            has_employee_term = any(term in narration_lower for term in employee_terms)
            has_salary_term = any(term in narration_lower for term in salary_terms)
            
            # Check for monthly/payment terms
            monthly_terms = ['monthly', 'month', 'periodic', 'regular']
            has_monthly_term = any(term in narration_lower for term in monthly_terms)
            
            # Combined checks
            if (has_employee_term and has_salary_term) or (has_monthly_term and has_salary_term):
                logger.info(f"MT103 salary context detected: {narration}")
                enhanced_result = self._create_enhanced_result(result, 'SALA', 0.95, "MT103 salary context")
                enhanced_result['category_purpose_code'] = "SALA"
                enhanced_result['category_confidence'] = 0.99
                enhanced_result['category_enhancement_applied'] = "salary_category_mapping"
                return enhanced_result
                
            # Check for semantic similarity with salary-related terms
            if self.matcher:
                salary_similarity = self.matcher.semantic_similarity_with_terms(narration_lower, self.semantic_terms)
                logger.debug(f"Salary semantic similarity: {salary_similarity:.4f}")
                
                if salary_similarity >= 0.7:
                    logger.info(f"High semantic similarity to salary terms: {salary_similarity:.4f}")
                    enhanced_result = self._create_enhanced_result(result, 'SALA', 0.9, f"Semantic similarity: {salary_similarity:.4f}")
                    enhanced_result['category_purpose_code'] = "SALA"
                    enhanced_result['category_confidence'] = 0.99
                    enhanced_result['category_enhancement_applied'] = "salary_category_mapping"
                    return enhanced_result

        # No salary pattern detected
        logger.debug("No salary pattern detected")
        return result

    def should_override_classification(self, result, narration):
        """
        Determine if salary classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()
        purpose_code = result.get('purpose_code', 'OTHR')
        confidence = result.get('confidence', 0.0)

        # Check for strong salary context
        salary_terms = ['salary', 'wage', 'payroll', 'compensation', 'remuneration', 'employee payment', 'staff payment']
        salary_count = sum(1 for term in salary_terms if term in narration_lower)

        # If multiple salary terms are present, likely salary-related
        if salary_count >= 2:
            # Don't override if confidence is very high
            if confidence >= 0.9:
                return False

            # Override OTHR or low confidence classifications
            if purpose_code == 'OTHR' or confidence < 0.7:
                return True

            # Override CCRD with any confidence (common misclassification)
            if purpose_code == 'CCRD':
                return True

        # Don't override other classifications unless very strong evidence
        return False
