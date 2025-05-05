"""
Interbank Enhancer for Purpose Classification

This enhancer specializes in identifying and correctly classifying interbank transactions.
"""

import re
import logging
from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer

# Set up logging
logger = logging.getLogger(__name__)

class InterbankEnhancerSemantic(SemanticEnhancer):
    """
    Enhancer for interbank transactions.

    This enhancer specializes in identifying and correctly classifying interbank transactions
    based on semantic understanding of the narration and message type.
    """

    def __init__(self, matcher=None):
        """
        Initialize the InterbankEnhancerSemantic.

        Args:
            matcher: Optional SemanticPatternMatcher instance to use
        """
        super().__init__(matcher=matcher)

        # Define interbank-related terms
        self.interbank_terms = [
            "interbank", "inter-bank", "bank to bank", "bank-to-bank",
            "correspondent", "nostro", "vostro", "loro", "financial institution",
            "bank transfer", "bank payment", "bank settlement", "bank clearing",
            "clearing system", "settlement system", "payment system",
            "rtgs", "real time gross settlement", "chaps", "fedwire", "target2",
            "chips", "swift", "bank wire", "wire transfer", "bank wire transfer",
            "bank settlement", "bank liquidity", "liquidity management",
            "bank funding", "bank reserves", "reserve requirement", "reserve position",
            "bank position", "bank balance", "bank account", "correspondent account",
            "correspondent banking", "correspondent relationship", "correspondent bank",
            "bank relationship", "bank network", "bank connection", "bank link",
            "bank channel", "bank corridor", "bank route", "bank path",
            "bank gateway", "bank portal", "bank interface", "bank access",
            "bank service", "bank facility", "bank arrangement", "bank agreement",
            "bank contract", "bank deal", "bank transaction", "bank operation",
            "bank activity", "bank business", "bank commerce", "bank trade",
            "bank exchange", "bank swap", "bank switch", "bank shift",
            "bank movement", "bank flow", "bank stream", "bank current",
            "bank circulation", "bank distribution", "bank allocation", "bank assignment",
            "bank designation", "bank appointment", "bank nomination", "bank selection",
            "bank choice", "bank option", "bank alternative", "bank preference",
            "bank priority", "bank rank", "bank order", "bank sequence",
            "bank series", "bank succession", "bank progression", "bank advance",
            "bank promotion", "bank elevation", "bank upgrade", "bank improvement",
            "bank enhancement", "bank augmentation", "bank amplification", "bank magnification",
            "bank intensification", "bank reinforcement", "bank strengthening", "bank fortification",
            "bank consolidation", "bank unification", "bank integration", "bank incorporation",
            "bank assimilation", "bank absorption", "bank merger", "bank acquisition",
            "bank takeover", "bank purchase", "bank procurement", "bank obtainment",
            "bank attainment", "bank achievement", "bank accomplishment", "bank realization",
            "bank fulfillment", "bank completion", "bank conclusion", "bank termination",
            "bank cessation", "bank discontinuation", "bank interruption", "bank suspension",
            "bank pause", "bank break", "bank halt", "bank stop"
        ]

        # Define patterns for interbank transactions
        self.interbank_patterns = [
            r'\binterbank\b',
            r'\binter-bank\b',
            r'\bbank\s+to\s+bank\b',
            r'\bbank-to-bank\b',
            r'\bcorrespondent\b',
            r'\bnostro\b',
            r'\bvostro\b',
            r'\bloro\b',
            r'\bfinancial\s+institution\b',
            r'\bbank\s+transfer\b',
            r'\bbank\s+payment\b',
            r'\bbank\s+settlement\b',
            r'\bbank\s+clearing\b',
            r'\bclearing\s+system\b',
            r'\bsettlement\s+system\b',
            r'\bpayment\s+system\b',
            r'\brtgs\b',
            r'\breal\s+time\s+gross\s+settlement\b',
            r'\bchaps\b',
            r'\bfedwire\b',
            r'\btarget2\b',
            r'\bchips\b',
            r'\bswift\b',
            r'\bbank\s+wire\b',
            r'\bwire\s+transfer\b',
            r'\bbank\s+wire\s+transfer\b',
            r'\bbank\s+settlement\b',
            r'\bbank\s+liquidity\b',
            r'\bliquidity\s+management\b',
            r'\bbank\s+funding\b',
            r'\bbank\s+reserves\b',
            r'\breserve\s+requirement\b',
            r'\breserve\s+position\b',
            r'\bbank\s+position\b',
            r'\bbank\s+balance\b',
            r'\bbank\s+account\b',
            r'\bcorrespondent\s+account\b',
            r'\bcorrespondent\s+banking\b',
            r'\bcorrespondent\s+relationship\b',
            r'\bcorrespondent\s+bank\b',
            r'\bbank\s+relationship\b',
            r'\bbank\s+network\b',
            r'\bbank\s+connection\b',
            r'\bbank\s+link\b',
            r'\bbank\s+channel\b',
            r'\bbank\s+corridor\b',
            r'\bbank\s+route\b',
            r'\bbank\s+path\b',
            r'\bbank\s+gateway\b',
            r'\bbank\s+portal\b',
            r'\bbank\s+interface\b',
            r'\bbank\s+access\b',
            r'\bbank\s+service\b',
            r'\bbank\s+facility\b',
            r'\bbank\s+arrangement\b',
            r'\bbank\s+agreement\b',
            r'\bbank\s+contract\b',
            r'\bbank\s+deal\b',
            r'\bbank\s+transaction\b',
            r'\bbank\s+operation\b',
            r'\bbank\s+activity\b',
            r'\bbank\s+business\b',
            r'\bbank\s+commerce\b',
            r'\bbank\s+trade\b',
            r'\bbank\s+exchange\b',
            r'\bbank\s+swap\b',
            r'\bbank\s+switch\b',
            r'\bbank\s+shift\b',
            r'\bbank\s+movement\b',
            r'\bbank\s+flow\b',
            r'\bbank\s+stream\b',
            r'\bbank\s+current\b',
            r'\bbank\s+circulation\b',
            r'\bbank\s+distribution\b',
            r'\bbank\s+allocation\b',
            r'\bbank\s+assignment\b',
            r'\bbank\s+designation\b',
            r'\bbank\s+appointment\b',
            r'\bbank\s+nomination\b',
            r'\bbank\s+selection\b',
            r'\bbank\s+choice\b',
            r'\bbank\s+option\b',
            r'\bbank\s+alternative\b',
            r'\bbank\s+preference\b',
            r'\bbank\s+priority\b',
            r'\bbank\s+rank\b',
            r'\bbank\s+order\b',
            r'\bbank\s+sequence\b',
            r'\bbank\s+series\b',
            r'\bbank\s+succession\b',
            r'\bbank\s+progression\b',
            r'\bbank\s+advance\b',
            r'\bbank\s+promotion\b',
            r'\bbank\s+elevation\b',
            r'\bbank\s+upgrade\b',
            r'\bbank\s+improvement\b',
            r'\bbank\s+enhancement\b',
            r'\bbank\s+augmentation\b',
            r'\bbank\s+amplification\b',
            r'\bbank\s+magnification\b',
            r'\bbank\s+intensification\b',
            r'\bbank\s+reinforcement\b',
            r'\bbank\s+strengthening\b',
            r'\bbank\s+fortification\b',
            r'\bbank\s+consolidation\b',
            r'\bbank\s+unification\b',
            r'\bbank\s+integration\b',
            r'\bbank\s+incorporation\b',
            r'\bbank\s+assimilation\b',
            r'\bbank\s+absorption\b',
            r'\bbank\s+merger\b',
            r'\bbank\s+acquisition\b',
            r'\bbank\s+takeover\b',
            r'\bbank\s+purchase\b',
            r'\bbank\s+procurement\b',
            r'\bbank\s+obtainment\b',
            r'\bbank\s+attainment\b',
            r'\bbank\s+achievement\b',
            r'\bbank\s+accomplishment\b',
            r'\bbank\s+realization\b',
            r'\bbank\s+fulfillment\b',
            r'\bbank\s+completion\b',
            r'\bbank\s+conclusion\b',
            r'\bbank\s+termination\b',
            r'\bbank\s+cessation\b',
            r'\bbank\s+discontinuation\b',
            r'\bbank\s+interruption\b',
            r'\bbank\s+suspension\b',
            r'\bbank\s+pause\b',
            r'\bbank\s+break\b',
            r'\bbank\s+halt\b',
            r'\bbank\s+stop\b'
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.interbank_patterns]

    def enhance(self, narration, purpose_code=None, confidence=None, category_purpose_code=None, category_confidence=None, message_type=None):
        """
        Enhance the purpose code classification for interbank transactions.

        Args:
            narration (str): The narration text to analyze.
            purpose_code (str, optional): The predicted purpose code.
            confidence (float, optional): The confidence of the prediction.
            category_purpose_code (str, optional): The predicted category purpose code.
            category_confidence (float, optional): The confidence of the category prediction.
            message_type (str, optional): The message type if already known.

        Returns:
            dict: A dictionary with enhanced classification.
        """
        # Create a result dictionary to store enhanced classification
        result = {
            'purpose_code': purpose_code,
            'confidence': confidence,
            'category_purpose_code': category_purpose_code,
            'category_confidence': category_confidence,
            'enhancement_applied': None
        }

        # If no purpose code or confidence provided, return the original result
        if not purpose_code or not confidence:
            return result

        # Check if the message type is MT202 or MT205, which are commonly used for interbank transfers
        is_interbank_message_type = message_type in ['MT202', 'MT205', 'MT202COV', 'MT205COV']

        # Check if the narration contains interbank-related terms
        pattern_match = any(pattern.search(narration) for pattern in self.compiled_patterns)

        # Special case for RTGS (Real-Time Gross Settlement)
        if 'rtgs' in narration.lower() or 'real time gross settlement' in narration.lower():
            pattern_match = True

        # Special case for financial institutions
        if 'financial institution' in narration.lower() and ('between' in narration.lower() or 'payment' in narration.lower() or 'transfer' in narration.lower()):
            pattern_match = True

        # Check for semantic similarity to interbank terms
        semantic_match = False
        semantic_score = 0.0

        if self.semantic_pattern_matcher:
            # Calculate semantic similarity to interbank terms
            for term in self.interbank_terms:
                score = self.semantic_pattern_matcher.calculate_similarity(narration, term)
                if score > semantic_score:
                    semantic_score = score

            # If semantic score is high enough, consider it a match
            if semantic_score >= 0.7:
                semantic_match = True

        # If the message type is interbank-related or the narration contains interbank-related terms,
        # or if there's a high semantic similarity to interbank terms, enhance the purpose code
        if is_interbank_message_type or pattern_match or semantic_match:
            # If the confidence is already high and the purpose code is already INTC, don't change it
            if purpose_code == 'INTC' and confidence >= 0.9:
                return result

            # Otherwise, enhance the purpose code to INTC with high confidence
            result['purpose_code'] = 'INTC'
            result['confidence'] = 0.95
            result['category_purpose_code'] = 'INTC'
            result['category_confidence'] = 0.95
            result['enhancer'] = 'interbank'
            result['enhanced'] = True

            # Add reason for the enhancement
            if is_interbank_message_type:
                result['reason'] = f"Enhanced based on interbank message type: {message_type}"
            elif pattern_match:
                result['reason'] = "Enhanced based on interbank-related terms in narration"
            elif semantic_match:
                result['reason'] = f"Enhanced based on semantic similarity to interbank terms (score: {semantic_score:.2f})"

        return result
