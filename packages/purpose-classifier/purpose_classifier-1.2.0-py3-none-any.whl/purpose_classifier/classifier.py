"""
Interbank domain enhancer for SWIFT message classification.
This file contains only the InterbankDomainEnhancer class which is used by the LightGBMPurposeClassifier.
The full PurposeClassifier implementation has been archived.
"""

import re

class InterbankDomainEnhancer:
    """Enhances classification for interbank-related payments"""

    def __init__(self):
        # Interbank-specific keywords with weights
        self.interbank_keywords = {
            # Direct interbank indicators (weight: 3)
            "interbank transfer": 3,
            "interbank payment": 3,
            "interbank settlement": 3,
            "interbank funding": 3,
            "interbank loan": 3,
            "interbank deposit": 3,
            "interbank placement": 3,
            "nostro account": 3,
            "vostro account": 3,
            "loro account": 3,
            "correspondent banking": 3,
            "treasury operation": 3,
            "money market transaction": 3,
            "forex settlement": 3,

            # Banking operations (weight: 2.5)
            "clearing system": 2.5,
            "settlement system": 2.5,
            "payment system": 2.5,
            "liquidity management": 2.5,
            "cash management": 2.5,
            "balance management": 2.5,
            "account funding": 2.5,
            "account rebalancing": 2.5,
            "position adjustment": 2.5,
            "position netting": 2.5,
            "position settlement": 2.5,
            "position reconciliation": 2.5,

            # Banking terms (weight: 2)
            "bank-to-bank": 2,
            "correspondent": 2,
            "nostro": 2,
            "vostro": 2,
            "loro": 2,
            "treasury": 2,
            "money market": 2,
            "forex": 2,
            "foreign exchange": 2,
            "currency swap": 2,
            "interest rate swap": 2,

            # Banking contexts (weight: 1.5)
            "interbank": 1.5,
            "clearing": 1.5,
            "settlement": 1.5,
            "funding": 1.5,
            "liquidity": 1.5,
            "cash": 1.5,
            "balance": 1.5,
            "position": 1.5,
            "exposure": 1.5,
            "limit": 1.5,

            # Banking-related terms (weight: 1)
            "bank": 1,
            "financial institution": 1,
            "central bank": 1,
            "reserve bank": 1,
            "monetary authority": 1,
            "banking": 1,
            "transaction": 1,
            "operation": 1,
            "transfer": 1,
            "payment": 1
        }

        # Individual word triggers with lower weights
        self.word_triggers = {
            "interbank": 1.5,
            "bank": 1.5,
            "banking": 1.5,
            "nostro": 1.0,
            "vostro": 1.0,
            "loro": 1.0,
            "correspondent": 1.0,
            "treasury": 1.0,
            "settlement": 1.0,
            "clearing": 0.8,
            "funding": 0.8,
            "liquidity": 0.8,
            "position": 0.8,
            "balance": 0.8,
            "forex": 0.7,
            "foreign exchange": 0.7,
            "money market": 0.7,
            "swap": 0.7,
            "financial": 0.7,
            "institution": 0.6,
            "central": 0.6,
            "reserve": 0.6,
            "monetary": 0.6,
            "authority": 0.6,
            "system": 0.5,
            "account": 0.5,
            "transfer": 0.5,
            "payment": 0.5,
            "transaction": 0.5
        }

        # Confidence thresholds for different levels of processing
        self.confidence_thresholds = {
            "high": 0.65,   # No intervention needed
            "medium": 0.35, # Apply domain-specific enhancement
            "low": 0.15     # Fall back to explicit keyword matching
        }

        # Purpose code mapping for interbank transactions
        self.interbank_purpose_mappings = {
            "interbank transfer": "INTC",   # Intra-Company Payment
            "interbank payment": "INTC",    # Intra-Company Payment
            "interbank settlement": "INTC", # Intra-Company Payment
            "interbank funding": "INTC",    # Intra-Company Payment
            "interbank loan": "INTC",       # Intra-Company Payment
            "interbank deposit": "INTC",    # Intra-Company Payment
            "interbank placement": "INTC",  # Intra-Company Payment
            "nostro account": "INTC",       # Intra-Company Payment
            "vostro account": "INTC",       # Intra-Company Payment
            "loro account": "INTC",         # Intra-Company Payment
            "correspondent banking": "INTC", # Intra-Company Payment
            "treasury operation": "INTC",   # Intra-Company Payment
            "money market transaction": "INTC", # Intra-Company Payment
            "forex settlement": "FREX",     # Foreign Exchange
            "foreign exchange": "FREX",     # Foreign Exchange
            "currency swap": "FREX",        # Foreign Exchange
            "fx transaction": "FREX",       # Foreign Exchange
            "fx settlement": "FREX",        # Foreign Exchange
            "fx trade": "FREX",             # Foreign Exchange
            "currency trade": "FREX",       # Foreign Exchange
            "currency transaction": "FREX", # Foreign Exchange
            "liquidity management": "INTC", # Intra-Company Payment
            "cash management": "INTC",      # Intra-Company Payment
            "balance management": "INTC",   # Intra-Company Payment
            "position adjustment": "INTC"   # Intra-Company Payment
        }

    def score_interbank_relevance(self, narration):
        """
        Score how relevant a narration is to interbank domain
        Returns a score and list of matched keywords
        """
        if not narration:
            return 0, []

        narration_lower = narration.lower()
        score = 0
        matched_keywords = []

        # 1. First check for exact phrase matches (highest confidence)
        for keyword, weight in self.interbank_keywords.items():
            if keyword in narration_lower:
                score += weight
                matched_keywords.append(keyword)

        # 2. Check for individual word triggers if no strong matches yet
        # Only apply if we don't have a strong match already (score < 2)
        if score < 2:
            words = set(re.findall(r'\b\w+\b', narration_lower))
            for word, weight in self.word_triggers.items():
                if word in words:
                    score += weight
                    matched_keywords.append(f"word:{word}")

        # 3. Check for specific combinations that indicate interbank domains
        if "interbank" in narration_lower and any(term in narration_lower for term in ["transfer", "payment", "settlement", "funding", "loan"]):
            score += 1.5
            matched_keywords.append("interbank+transfer/payment/settlement/funding/loan")

        if "nostro" in narration_lower and any(term in narration_lower for term in ["account", "balance", "transfer", "payment", "settlement"]):
            score += 1.5
            matched_keywords.append("nostro+account/balance/transfer/payment/settlement")

        if "forex" in narration_lower and any(term in narration_lower for term in ["settlement", "trade", "transaction", "exchange", "swap"]):
            score += 1.5
            matched_keywords.append("forex+settlement/trade/transaction/exchange/swap")

        # Normalize score to 0-1 range if we found matches
        if matched_keywords:
            # Lower denominator to make it easier to reach higher scores
            score = min(score / 8, 1.0)  # Cap at 1.0

        return score, matched_keywords

    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification based on domain-specific knowledge and message type context

        Args:
            result: The classification result to enhance
            narration: The narration text
            message_type: Optional message type (MT103, MT202, MT202COV, MT205, MT205COV)
        """
        # Get interbank relevance score and matched keywords first
        interbank_score, matched_keywords = self.score_interbank_relevance(narration)

        # Always add interbank score and keywords to the result for analysis
        result['interbank_score'] = interbank_score
        result['interbank_keywords'] = matched_keywords

        # Store original values
        original_purpose = result.get('purpose_code', 'OTHR')
        original_conf = result.get('confidence', 0.3)

        # Check for message type context - MT202 and MT205 are typically interbank messages
        is_interbank_message_type = message_type in ['MT202', 'MT202COV', 'MT205', 'MT205COV']

        # Boost interbank score for interbank message types
        if is_interbank_message_type:
            interbank_score = min(interbank_score * 1.5, 1.0)
            result['interbank_score_boosted'] = interbank_score
            result['message_type_context'] = message_type

            # MT202 and MT202COV are typically used for interbank transfers
            if message_type in ['MT202', 'MT202COV']:
                # Strong interbank indicators in MT202/MT202COV
                interbank_keywords = [
                    'interbank', 'nostro', 'vostro', 'correspondent', 'liquidity',
                    'treasury', 'position', 'funding', 'settlement', 'clearing',
                    'cash management', 'cash position', 'cash flow', 'cash transfer'
                ]

                # Check for interbank keywords in MT202/MT202COV
                if any(keyword in narration.lower() for keyword in interbank_keywords):
                    # Override with INTC with high confidence
                    result['purpose_code'] = 'INTC'
                    result['confidence'] = 0.98
                    result['enhancement_applied'] = 'interbank_message_type_override'
                    result['category_purpose_code'] = 'INTC'
                    result['category_confidence'] = 0.98
                    return result

                # Check for foreign exchange settlement in MT202/MT202COV
                forex_keywords = [
                    'forex', 'fx', 'foreign exchange', 'currency exchange', 'exchange rate',
                    'currency conversion', 'currency trade', 'currency settlement', 'fx settlement',
                    'forex settlement', 'foreign exchange settlement'
                ]

                # Special case for forex settlement
                if 'forex settlement' in narration.lower() or 'foreign exchange settlement' in narration.lower():
                    # Override with FREX with high confidence
                    result['purpose_code'] = 'FREX'
                    result['confidence'] = 0.98
                    result['enhancement_applied'] = 'forex_settlement_override'
                    result['category_purpose_code'] = 'FREX'
                    result['category_confidence'] = 0.98
                    return result

                # Check for USD/EUR or EUR/GBP patterns which indicate forex
                if re.search(r'(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)/(USD|EUR|GBP|JPY|CHF|AUD|CAD|NZD)', narration):
                    # Override with FREX with high confidence
                    result['purpose_code'] = 'FREX'
                    result['confidence'] = 0.98
                    result['enhancement_applied'] = 'currency_pair_override'
                    result['category_purpose_code'] = 'FREX'
                    result['category_confidence'] = 0.98
                    return result

                # Check for other forex keywords
                if any(keyword in narration.lower() for keyword in forex_keywords):
                    # Override with FREX with high confidence
                    result['purpose_code'] = 'FREX'
                    result['confidence'] = 0.98
                    result['enhancement_applied'] = 'forex_message_type_override'
                    result['category_purpose_code'] = 'FREX'
                    result['category_confidence'] = 0.98
                    return result

            # MT205 and MT205COV are typically used for financial institution transfers
            if message_type in ['MT205', 'MT205COV']:
                # Strong treasury indicators in MT205/MT205COV
                treasury_keywords = [
                    'treasury', 'liquidity', 'cash management', 'cash position', 'cash flow',
                    'cash transfer', 'position', 'funding', 'settlement', 'clearing'
                ]

                # Check for treasury keywords in MT205/MT205COV
                if any(keyword in narration.lower() for keyword in treasury_keywords):
                    # Override with TREA with high confidence
                    result['purpose_code'] = 'TREA'
                    result['confidence'] = 0.98
                    result['enhancement_applied'] = 'treasury_message_type_override'
                    result['category_purpose_code'] = 'TREA'
                    result['category_confidence'] = 0.98
                    return result

        # Skip enhancement if confidence is already high AND interbank score isn't very high
        # This allows high-confidence interbank payments to still get enhancement
        if result['confidence'] >= self.confidence_thresholds["high"] and interbank_score < 0.5:
            # Special case: If it's an interbank message type with CASH purpose code, consider changing to INTC
            if is_interbank_message_type and original_purpose == 'CASH' and 'liquidity' in narration.lower():
                result['purpose_code'] = "INTC"
                result['purpose_description'] = "Intra-Company Payment"
                result['enhancement_applied'] = "message_type_context_override"
                result['confidence'] = min(original_conf * 1.2, 0.95)
                return result
            return result

        # Lower threshold for applying enhancement
        if interbank_score < 0.25 and not is_interbank_message_type:
            return result

        # Determine if we need to override or enhance the classification
        if interbank_score >= 0.5 or is_interbank_message_type:
            # High interbank relevance, determine the appropriate interbank type
            # Check if any forex-related keywords were matched
            forex_keywords = [kw for kw in matched_keywords if any(term in kw.lower() for term in
                             ["forex", "fx", "foreign exchange", "currency", "swap"])]

            # Check for specific forex patterns in the narration
            forex_patterns = ["currency", "exchange rate", "fx rate", "forex", "foreign exchange", "swap"]
            has_forex_pattern = any(pattern in narration.lower() for pattern in forex_patterns)

            if forex_keywords or has_forex_pattern:
                # Override to FREX (Foreign Exchange) with high confidence
                result['purpose_code'] = "FREX"
                result['purpose_description'] = "Foreign Exchange"
                result['forex_patterns_matched'] = has_forex_pattern
            else:
                # Override to INTC (Intra-Company Payment) with high confidence
                # Special case: If it's CASH and an interbank message type, keep as CASH
                if original_purpose == 'CASH' and is_interbank_message_type and 'cash management' in narration.lower():
                    # Keep as CASH but add enhancement info
                    result['enhancement_applied'] = "interbank_cash_management"
                else:
                    result['purpose_code'] = "INTC"
                    result['purpose_description'] = "Intra-Company Payment"

            # Blend original confidence with interbank score - give more weight to interbank_score
            adjusted_conf = (original_conf * 0.2) + (interbank_score * 0.8)
            result['confidence'] = min(adjusted_conf, 0.95)  # Cap at 0.95

            # Add enhancement info
            if 'enhancement_applied' not in result:
                result['enhancement_applied'] = "interbank_domain_override"
                if is_interbank_message_type:
                    result['enhancement_applied'] = "interbank_message_type_override"

        elif interbank_score > 0.35 or is_interbank_message_type:
            # Medium interbank relevance, adjust confidence if prediction is INTC or FREX
            if original_purpose in ["INTC", "FREX", "CASH"]:
                # Boost confidence for interbank classification
                result['confidence'] = min(original_conf * 1.5, 0.9)
                result['enhancement_applied'] = "interbank_domain_boost"
            else:
                # Suggest appropriate interbank type as an alternative
                forex_keywords = [kw for kw in matched_keywords if any(term in kw.lower() for term in
                                ["forex", "fx", "foreign exchange", "currency", "swap"])]

                if forex_keywords:
                    result['alternative_purpose'] = "FREX"
                    result['alternative_description'] = "Foreign Exchange"
                else:
                    result['alternative_purpose'] = "INTC"
                    result['alternative_description'] = "Intra-Company Payment"

                result['alternative_confidence'] = interbank_score
                result['interbank_relevance'] = "medium"
        elif interbank_score > 0.25:
            # Weak interbank relevance, just add interbank score info without changing classification
            result['interbank_relevance'] = "weak"

        return result







    def predict(self, text_or_message):
        """
        Predict purpose code and category purpose code from text or MT message.
        Uses caching if enabled in environment settings.

        Args:
            text_or_message: Text narration or full MT message

        Returns:
            Dictionary with prediction results
        """
        try:
            # Check if input is a full MT message or just narration text
            if isinstance(text_or_message, str) and ('{1:' in text_or_message and '{4:' in text_or_message):
                message_type, narration = self._extract_from_message(text_or_message)
                if not narration:
                    self.logger.warning("Failed to extract narration from message")
                    return {
                        'purpose_code': self._get_fallback_code(),
                        'purpose_description': self.purpose_codes.get(self._get_fallback_code(), 'Other'),
                        'category_purpose_code': 'OTHR',
                        'category_purpose_description': self.category_purpose_codes.get('OTHR', 'Other'),
                        'confidence': 0.0,
                        'message_type': message_type,
                        'extracted_narration': None,
                        'error': 'Failed to extract narration'
                    }
            else:
                narration = text_or_message
                message_type = None

            # Use cached prediction implementation if enabled
            result = self.predict_cached(narration, message_type)

            # Check if auto domain enhancements should be applied
            should_enhance_tech = False
            should_enhance_education = False
            should_enhance_services = False
            should_enhance_trade = False
            should_enhance_interbank = False
            should_enhance_category_purpose = False

            # Auto tech enhancement check
            if self.auto_tech_enhance and narration:
                # Always create a fresh instance of the tech enhancer to ensure we use the latest code
                # This prevents issues with cached or saved versions of the enhancer
                tech_enhancer = TechDomainEnhancer()

                # Get the tech score to determine if enhancement is needed
                tech_score, tech_keywords = tech_enhancer.score_tech_relevance(narration)

                # Decide if enhancement should be applied
                # Use a threshold to determine if this is tech-related enough (40% relevance)
                should_enhance_tech = tech_score >= 0.4

                # Add tech analysis data regardless of whether we apply enhancement
                result['tech_score'] = tech_score
                result['tech_keywords'] = tech_keywords
                result['auto_tech_analysis'] = True

                if should_enhance_tech:
                    self.logger.info(f"Auto-detected tech content (score: {tech_score:.2f}), applying enhancement")
                    result['auto_enhancement'] = True
                    result = tech_enhancer.enhance_classification(result, narration)

            # Apply tech domain enhancement if explicitly enabled
            elif self.use_tech_enhancer and narration:
                self.logger.debug("Applying tech domain enhancement")

                # Always create a fresh instance of the tech enhancer
                tech_enhancer = TechDomainEnhancer()

                result = tech_enhancer.enhance_classification(result, narration)

            # Auto education enhancement check
            if self.auto_education_enhance and narration:
                # Always create a fresh instance of the education enhancer
                education_enhancer = EducationDomainEnhancer()

                # Get the education score to determine if enhancement is needed
                education_score, education_keywords = education_enhancer.score_education_relevance(narration)

                # Decide if enhancement should be applied (40% relevance threshold)
                should_enhance_education = education_score >= 0.4

                # Add education analysis data regardless of whether we apply enhancement
                result['education_score'] = education_score
                result['education_keywords'] = education_keywords
                result['auto_education_analysis'] = True

                if should_enhance_education:
                    self.logger.info(f"Auto-detected education content (score: {education_score:.2f}), applying enhancement")
                    result['auto_enhancement'] = True
                    result = education_enhancer.enhance_classification(result, narration)

            # Apply education domain enhancement if explicitly enabled
            elif self.use_education_enhancer and narration:
                self.logger.debug("Applying education domain enhancement")

                # Always create a fresh instance of the education enhancer
                education_enhancer = EducationDomainEnhancer()

                result = education_enhancer.enhance_classification(result, narration)

            # Auto services enhancement check
            if self.auto_services_enhance and narration:
                # Always create a fresh instance of the services enhancer
                services_enhancer = ServicesDomainEnhancer()

                # Get the services score to determine if enhancement is needed
                services_score, services_keywords = services_enhancer.score_services_relevance(narration)

                # Decide if enhancement should be applied (40% relevance threshold)
                should_enhance_services = services_score >= 0.4

                # Add services analysis data regardless of whether we apply enhancement
                result['services_score'] = services_score
                result['services_keywords'] = services_keywords
                result['auto_services_analysis'] = True

                if should_enhance_services:
                    self.logger.info(f"Auto-detected services content (score: {services_score:.2f}), applying enhancement")
                    result['auto_enhancement'] = True
                    result = services_enhancer.enhance_classification(result, narration)

            # Apply services domain enhancement if explicitly enabled
            elif self.use_services_enhancer and narration:
                self.logger.debug("Applying services domain enhancement")

                # Always create a fresh instance of the services enhancer
                services_enhancer = ServicesDomainEnhancer()

                result = services_enhancer.enhance_classification(result, narration)

            # Auto trade enhancement check
            if self.auto_trade_enhance and narration:
                # Always create a fresh instance of the trade enhancer
                trade_enhancer = TradeDomainEnhancer()

                # Get the trade score to determine if enhancement is needed
                trade_score, trade_keywords = trade_enhancer.score_trade_relevance(narration)

                # Decide if enhancement should be applied (40% relevance threshold)
                should_enhance_trade = trade_score >= 0.4

                # Add trade analysis data regardless of whether we apply enhancement
                result['trade_score'] = trade_score
                result['trade_keywords'] = trade_keywords
                result['auto_trade_analysis'] = True

                if should_enhance_trade:
                    self.logger.info(f"Auto-detected trade content (score: {trade_score:.2f}), applying enhancement")
                    result['auto_enhancement'] = True
                    result = trade_enhancer.enhance_classification(result, narration)

            # Apply trade domain enhancement if explicitly enabled
            elif self.use_trade_enhancer and narration:
                self.logger.debug("Applying trade domain enhancement")

                # Always create a fresh instance of the trade enhancer
                trade_enhancer = TradeDomainEnhancer()

                result = trade_enhancer.enhance_classification(result, narration)

            # Auto interbank enhancement check
            if self.auto_interbank_enhance and narration:
                # Always create a fresh instance of the interbank enhancer
                interbank_enhancer = InterbankDomainEnhancer()

                # Get the interbank score to determine if enhancement is needed
                interbank_score, interbank_keywords = interbank_enhancer.score_interbank_relevance(narration)

                # Decide if enhancement should be applied (40% relevance threshold)
                should_enhance_interbank = interbank_score >= 0.4

                # Add interbank analysis data regardless of whether we apply enhancement
                result['interbank_score'] = interbank_score
                result['interbank_keywords'] = interbank_keywords
                result['auto_interbank_analysis'] = True

                if should_enhance_interbank:
                    self.logger.info(f"Auto-detected interbank content (score: {interbank_score:.2f}), applying enhancement")
                    result['auto_enhancement'] = True
                    result = interbank_enhancer.enhance_classification(result, narration)

            # Apply interbank domain enhancement if explicitly enabled
            elif self.use_interbank_enhancer and narration:
                self.logger.debug("Applying interbank domain enhancement")

                # Always create a fresh instance of the interbank enhancer
                interbank_enhancer = InterbankDomainEnhancer()

                result = interbank_enhancer.enhance_classification(result, narration)

            # Auto category purpose enhancement check
            if self.auto_category_purpose_enhance and narration:
                # Always create a fresh instance of the category purpose enhancer to ensure we use the latest code
                category_purpose_enhancer = CategoryPurposeDomainEnhancer()

                # Check if this is a category purpose-related payment
                category_score, _, _ = category_purpose_enhancer.score_category_relevance(narration)

                # Apply enhancement if score is above threshold - lower threshold to reduce OTHR usage
                should_enhance_category_purpose = category_score >= 0.25

                if should_enhance_category_purpose:
                    self.logger.info(f"Auto-detected category purpose content (score: {category_score:.2f}), applying enhancement")
                    result['auto_enhancement'] = True
                    result = category_purpose_enhancer.enhance_classification(result, narration)

            # Apply category purpose domain enhancement if explicitly enabled
            elif self.use_category_purpose_enhancer and narration:
                self.logger.debug("Applying category purpose domain enhancement")

                # Always create a fresh instance of the category purpose enhancer
                category_purpose_enhancer = CategoryPurposeDomainEnhancer()

                result = category_purpose_enhancer.enhance_classification(result, narration)

            # Auto transportation enhancement check
            if self.auto_transportation_enhance and narration:
                # Always create a fresh instance of the transportation enhancer
                transportation_enhancer = TransportationDomainEnhancer()

                # Get the transportation score to determine if enhancement is needed
                transportation_score, matched_keywords, _ = transportation_enhancer.score_transportation_relevance(narration)

                # Decide if enhancement should be applied (40% relevance threshold)
                should_enhance_transportation = transportation_score >= 0.4

                # Add transportation analysis data regardless of whether we apply enhancement
                result['transportation_score'] = transportation_score
                result['transportation_keywords'] = matched_keywords
                result['auto_transportation_analysis'] = True

                if should_enhance_transportation:
                    self.logger.info(f"Auto-detected transportation content (score: {transportation_score:.2f}), applying enhancement")
                    result['auto_enhancement'] = True
                    result = transportation_enhancer.enhance_classification(result, narration)

            # Apply transportation domain enhancement if explicitly enabled
            elif self.use_transportation_enhancer and narration:
                self.logger.debug("Applying transportation domain enhancement")

                # Always create a fresh instance of the transportation enhancer
                transportation_enhancer = TransportationDomainEnhancer()

                result = transportation_enhancer.enhance_classification(result, narration)

            # Auto financial services enhancement check
            if self.auto_financial_services_enhance and narration:
                # Always create a fresh instance of the financial services enhancer
                financial_services_enhancer = FinancialServicesDomainEnhancer()

                # Get the financial services score to determine if enhancement is needed
                financial_score, matched_keywords, _ = financial_services_enhancer.score_financial_relevance(narration)

                # Decide if enhancement should be applied (40% relevance threshold)
                should_enhance_financial = financial_score >= 0.4

                # Add financial services analysis data regardless of whether we apply enhancement
                result['financial_score'] = financial_score
                result['financial_keywords'] = matched_keywords
                result['auto_financial_analysis'] = True

                if should_enhance_financial:
                    self.logger.info(f"Auto-detected financial services content (score: {financial_score:.2f}), applying enhancement")
                    result['auto_enhancement'] = True
                    result = financial_services_enhancer.enhance_classification(result, narration)

            # Apply financial services domain enhancement if explicitly enabled
            elif self.use_financial_services_enhancer and narration:
                self.logger.debug("Applying financial services domain enhancement")

                # Always create a fresh instance of the financial services enhancer
                financial_services_enhancer = FinancialServicesDomainEnhancer()

                result = financial_services_enhancer.enhance_classification(result, narration)

            return result

        except Exception as e:
            self.logger.error(f"Error in prediction: {str(e)}")
            return {
                'purpose_code': self._get_fallback_code(),
                'purpose_description': self.purpose_codes.get(self._get_fallback_code(), 'Other'),
                'category_purpose_code': 'OTHR',
                'category_purpose_description': self.category_purpose_codes.get('OTHR', 'Other'),
                'confidence': 0.0,
                'message_type': None,
                'extracted_narration': narration if isinstance(narration, str) else None,
                'error': str(e)
            }

    def _predict_impl(self, narration, message_type=None):
        """
        Implementation of prediction logic.
        Can be cached with lru_cache decorator.

        Args:
            narration: Text narration
            message_type: Type of MT message (if known)

        Returns:
            Dictionary with prediction results
        """
        if not self.purpose_model:
            self.logger.error("Model not trained or loaded")
            raise RuntimeError("Model not trained or loaded")

        # Preprocess text
        processed_text = self.preprocessor.preprocess(narration)

        # Transform using existing vocabulary
        features = self.feature_extractor.transform([processed_text], message_types=[message_type] if message_type else None)

        # Predict purpose code
        purpose_probs = self.purpose_model.predict_proba(features)[0]
        purpose_idx = np.argmax(purpose_probs)
        purpose_code = self.purpose_model.classes_[purpose_idx]
        confidence = purpose_probs[purpose_idx]

        # Get top-3 predictions for more robust decision making
        top_indices = purpose_probs.argsort()[-3:][::-1]
        top_codes = [self.purpose_model.classes_[i] for i in top_indices]
        top_probs = [purpose_probs[i] for i in top_indices]

        result = {
            'purpose_code': purpose_code,
            'purpose_description': self.purpose_codes.get(purpose_code, 'Unknown'),
            'confidence': float(confidence),
            'message_type': message_type,
            'extracted_narration': narration,
            'top_purpose_codes': dict(zip(top_codes, [float(p) for p in top_probs])),
        }

        # Predict category purpose code if model is available
        if self.category_purpose_model:
            category_probs = self.category_purpose_model.predict_proba(features)[0]
            category_idx = np.argmax(category_probs)
            category_purpose_code = self.category_purpose_model.classes_[category_idx]
            category_confidence = category_probs[category_idx]

            # Get top-3 category predictions
            top_cat_indices = category_probs.argsort()[-3:][::-1]
            top_cat_codes = [self.category_purpose_model.classes_[i] for i in top_cat_indices]
            top_cat_probs = [category_probs[i] for i in top_cat_indices]

            # Ensure we never return 'nan' as a category purpose code
            if category_purpose_code == 'nan' or pd.isna(category_purpose_code):
                category_purpose_code = 'OTHR'

            result['category_purpose_code'] = category_purpose_code
            result['category_purpose_description'] = self.category_purpose_codes.get(category_purpose_code, 'Unknown')
            result['category_confidence'] = float(category_confidence)
            result['top_category_codes'] = dict(zip(top_cat_codes, [float(p) for p in top_cat_probs]))
        else:
            # Default to 'OTHR' if no category model
            result['category_purpose_code'] = 'OTHR'
            result['category_purpose_description'] = self.category_purpose_codes.get('OTHR', 'Other')
            result['category_confidence'] = 0.0

        # Check confidence threshold and apply fallback strategy if needed
        result = self._apply_fallback_strategy(result)

        # Try to detect payment type from text as an additional check
        detected_type = self.preprocessor.detect_payment_type(narration)
        if detected_type and result['confidence'] < 0.8:
            result['rule_based_suggestion'] = detected_type
            result['rule_based_description'] = self.purpose_codes.get(detected_type, "Unknown")

        return result

    def _apply_fallback_strategy(self, result):
        """
        Apply fallback strategies for low-confidence predictions

        Args:
            result: Prediction result dictionary

        Returns:
            Updated result with fallback applied if needed
        """
        confidence = result['confidence']

        # Check if prediction is below minimum confidence threshold
        if confidence < MODEL_SETTINGS['min_confidence']:
            self.logger.warning(f"Low confidence prediction: {confidence:.4f}")

            # Apply different strategies depending on how low the confidence is
            if confidence < MODEL_SETTINGS['fallback_threshold']:
                self.logger.warning(f"Below fallback threshold, applying fallback strategy: {self.fallback_strategy}")

                if self.fallback_strategy == 'most_frequent':
                    # Choose most frequent code from training data
                    if self.frequent_purpose_codes:
                        # Always use OTHR as fallback
                        result['purpose_code'] = 'OTHR'
                        result['purpose_description'] = self.purpose_codes.get('OTHR', 'Other Payment')
                        result['fallback_applied'] = 'most_frequent'
                    else:
                        # If no frequent codes available, use OTHR
                        result['purpose_code'] = 'OTHR'
                        result['purpose_description'] = self.purpose_codes.get('OTHR', 'Other Payment')
                        result['fallback_applied'] = 'default'

                elif self.fallback_strategy == 'rule_based':
                    # Try to infer from text using rule-based approach
                    detected_type = self.preprocessor.detect_payment_type(result['extracted_narration'])
                    if detected_type:
                        result['purpose_code'] = detected_type
                        result['purpose_description'] = self.purpose_codes.get(detected_type, 'Unknown')
                        result['fallback_applied'] = 'rule_based'
                    else:
                        result['purpose_code'] = self.fallback_default
                        result['purpose_description'] = self.purpose_codes.get(self.fallback_default, 'Other')
                        result['fallback_applied'] = 'default'

                else:
                    # Default fallback
                    result['purpose_code'] = self.fallback_default
                    result['purpose_description'] = self.purpose_codes.get(self.fallback_default, 'Other')
                    result['fallback_applied'] = 'default'

        return result

    def _get_fallback_code(self):
        """Get the appropriate fallback purpose code based on strategy"""
        if self.fallback_strategy == 'most_frequent' and self.frequent_purpose_codes:
            # Always use OTHR as fallback
            return 'OTHR'
        # Make sure we never return 'global' as a fallback code
        if self.fallback_default == 'global':
            return 'OTHR'
        return self.fallback_default

    def detect_message_type(self, message):
        """
        Detect the message type from a full SWIFT message.

        Args:
            message: Full SWIFT message

        Returns:
            Detected message type or None
        """
        if not isinstance(message, str):
            return None

        # Look for message type identifiers in the message
        if '{2:I103' in message:
            return 'MT103'
        elif '{2:I202COV' in message or 'COV-' in message:
            return 'MT202COV'
        elif '{2:I202' in message:
            return 'MT202'
        elif '{2:I205COV' in message:
            return 'MT205COV'
        elif '{2:I205' in message:
            return 'MT205'

        # Try additional pattern matching
        if ':20:' in message and ':32A:' in message and ':50' in message and ':59:' in message:
            # MT103 typically has these fields
            return 'MT103'

        if ':20:' in message and ':21:' in message and ':32A:' in message:
            # MT202 pattern
            if 'COV' in message:
                return 'MT202COV'
            return 'MT202'

        # Could not determine
        return None

    def _extract_from_message(self, message):
        """
        Extract narration and message type from a full MT message.

        Args:
            message: Full MT message string

        Returns:
            Tuple of (message_type, narration)
        """
        # Detect message type
        message_type = self.detect_message_type(message)

        if not message_type:
            self.logger.warning("Could not determine message type")
            # Default to MT103 for parsing
            message_type = 'MT103'

        # Use appropriate handler to extract narration
        handler = self.message_handlers.get(message_type)
        if handler:
            narration = handler(message)
            if narration:
                return message_type, narration

        # Fallback to generic extraction if handler failed or is missing
        mt_config = MESSAGE_TYPES.get(message_type, MESSAGE_TYPES['MT103'])
        pattern = mt_config['regex_pattern']

        matches = re.search(pattern, message, re.DOTALL)
        if matches:
            narration = matches.group(1).strip().replace('\n', ' ')
            return message_type, narration

        return message_type, None

    def _extract_mt103_narration(self, message):
        """Extract narration from MT103 message (field 70)"""
        pattern = r':70:(.*?)(?=:\d{2}[A-Z]:|$)'
        matches = re.search(pattern, message, re.DOTALL)
        if matches:
            return matches.group(1).strip().replace('\n', ' ')
        return None

    def _extract_mt202_narration(self, message):
        """Extract narration from MT202 message (field 72)"""
        pattern = r':72:(.*?)(?=:\d{2}[A-Z]:|$)'
        matches = re.search(pattern, message, re.DOTALL)
        if matches:
            return matches.group(1).strip().replace('\n', ' ')
        return None

    def _extract_mt202cov_narration(self, message):
        """Extract narration from MT202COV message (field 72)"""
        # Look for both standard field 72 and sequence B field 72
        patterns = [
            r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
            r'B]:.*?:72:(.*?)(?=:\d{2}[A-Z]:|$)'
        ]

        for pattern in patterns:
            matches = re.search(pattern, message, re.DOTALL)
            if matches:
                return matches.group(1).strip().replace('\n', ' ')

        return None

    def _extract_mt205_narration(self, message):
        """Extract narration from MT205 message (field 72)"""
        pattern = r':72:(.*?)(?=:\d{2}[A-Z]:|$)'
        matches = re.search(pattern, message, re.DOTALL)
        if matches:
            return matches.group(1).strip().replace('\n', ' ')
        return None

    def _extract_mt205cov_narration(self, message):
        """Extract narration from MT205COV message (field 72)"""
        # Similar to MT202COV but for MT205COV
        patterns = [
            r':72:(.*?)(?=:\d{2}[A-Z]:|$)',
            r'B]:.*?:72:(.*?)(?=:\d{2}[A-Z]:|$)'
        ]

        for pattern in patterns:
            matches = re.search(pattern, message, re.DOTALL)
            if matches:
                return matches.group(1).strip().replace('\n', ' ')

        return None

    def batch_predict(self, messages_or_texts):
        """
        Process a batch of messages or texts.

        Args:
            messages_or_texts: List of messages or narrations

        Returns:
            List of prediction results
        """
        self.logger.info(f"Processing batch of {len(messages_or_texts)} items")
        results = []

        for item in messages_or_texts:
            results.append(self.predict(item))

        return results

    def predict_with_tech_domain(self, text_or_message):
        """
        Predict purpose with tech domain enhancement, regardless of use_tech_enhancer setting.
        Useful for comparing standard and enhanced results.

        Args:
            text_or_message: Text narration or full MT message

        Returns:
            Dictionary with standard result and tech enhanced result
        """
        # Save original tech enhancer setting
        original_setting = self.use_tech_enhancer

        # Temporarily disable tech enhancer to get baseline prediction
        self.use_tech_enhancer = False
        standard_result = self.predict(text_or_message)

        # Create tech enhancer if not already present
        if not hasattr(self, 'tech_enhancer'):
            temp_enhancer = TechDomainEnhancer()
        else:
            temp_enhancer = self.tech_enhancer

        # Get narration if processing full message
        if isinstance(text_or_message, str) and ('{1:' in text_or_message and '{4:' in text_or_message):
            _, narration = self._extract_from_message(text_or_message)
        else:
            narration = text_or_message

        # Get tech score
        tech_score, tech_keywords = temp_enhancer.score_tech_relevance(narration)

        # Apply enhancement
        enhanced_result = temp_enhancer.enhance_classification(standard_result.copy(), narration)

        # Restore original setting
        self.use_tech_enhancer = original_setting

        # Return comparison
        return {
            'standard': standard_result,
            'enhanced': enhanced_result,
            'tech_score': tech_score,
            'tech_keywords': tech_keywords,
            'enhancement_applied': 'enhancement_applied' in enhanced_result,
            'narration': narration
        }

    def save(self, custom_path=None):
        """
        Save models and feature extractor to disk.

        Args:
            custom_path: Optional custom path to save model
        """
        if not self.purpose_model:
            self.logger.error("Cannot save: model not trained")
            raise RuntimeError("Model not trained")

        save_path = custom_path or MODEL_PATH

        # Handle case where dirname returns empty string (file in current directory)
        dir_name = os.path.dirname(save_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        # Update model version if not set
        if not self.model_version:
            self.model_version = {
                'timestamp': datetime.datetime.now().isoformat(),
                'environment': self.env,
                'purpose_model_type': type(self.purpose_model).__name__,
                'category_model_type': type(self.category_purpose_model).__name__ if self.category_purpose_model else None,
                'ensemble': self.use_ensemble,
                'tech_enhancer': self.use_tech_enhancer,
                'auto_tech_enhance': self.auto_tech_enhance,
                'education_enhancer': self.use_education_enhancer,
                'auto_education_enhance': self.auto_education_enhance,
                'services_enhancer': self.use_services_enhancer,
                'auto_services_enhance': self.auto_services_enhance,
                'trade_enhancer': self.use_trade_enhancer,
                'auto_trade_enhance': self.auto_trade_enhance,
                'interbank_enhancer': self.use_interbank_enhancer,
                'auto_interbank_enhance': self.auto_interbank_enhance,
                'category_purpose_enhancer': self.use_category_purpose_enhancer,
                'auto_category_purpose_enhance': self.auto_category_purpose_enhance,
                'transportation_enhancer': self.use_transportation_enhancer,
                'auto_transportation_enhance': self.auto_transportation_enhance,
                'financial_services_enhancer': self.use_financial_services_enhancer,
                'auto_financial_services_enhance': self.auto_financial_services_enhance
            }

        # Create model package with all necessary components
        model_package = {
            'purpose_model': self.purpose_model,
            'category_purpose_model': self.category_purpose_model,
            'feature_extractor': self.feature_extractor,
            'frequent_purpose_codes': self.frequent_purpose_codes,
            'fallback_strategy': self.fallback_strategy,
            'fallback_default': self.fallback_default,
            'use_tech_enhancer': self.use_tech_enhancer,
            'auto_tech_enhance': self.auto_tech_enhance,
            'use_education_enhancer': self.use_education_enhancer,
            'auto_education_enhance': self.auto_education_enhance,
            'use_services_enhancer': self.use_services_enhancer,
            'auto_services_enhance': self.auto_services_enhance,
            'use_trade_enhancer': self.use_trade_enhancer,
            'auto_trade_enhance': self.auto_trade_enhance,
            'use_interbank_enhancer': self.use_interbank_enhancer,
            'auto_interbank_enhance': self.auto_interbank_enhance,
            'use_transportation_enhancer': self.use_transportation_enhancer,
            'auto_transportation_enhance': self.auto_transportation_enhance,
            'use_financial_services_enhancer': self.use_financial_services_enhancer,
            'auto_financial_services_enhance': self.auto_financial_services_enhance,
            'version': self.model_version
        }

        # Verify the model package is a dictionary
        if not isinstance(model_package, dict):
            self.logger.error(f"Invalid model package type: {type(model_package)}")
            raise ValueError("Model package must be a dictionary")

        # Debug print
        self.logger.debug(f"Model package keys: {list(model_package.keys())}")

        try:
            # Save the model package
            model_file = save_path
            joblib.dump(model_package, model_file)
            self.logger.info(f"Model saved to {model_file}")

            # Save backup if enabled
            if self.env_settings['backup_enabled']:
                # Use the parent dir of the file's directory, or current dir if no parent
                save_dir = os.path.dirname(save_path)
                if save_dir:
                    backup_dir = os.path.join(os.path.dirname(save_dir), 'backups')
                else:
                    backup_dir = os.path.join(os.getcwd(), 'backups')

                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(
                    backup_dir,
                    f"model_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
                )
                # Use the same model_package we created for the original save
                joblib.dump(model_package, backup_path)
                self.logger.info(f"Model backup saved to {backup_path}")

            # Create version info
            if self.env_settings['model_version_file']:
                version_info = {
                    'path': model_file,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'environment': self.env,
                    'version': self.model_version
                }
                with open(self.env_settings['model_version_file'], 'w') as f:
                    json.dump(version_info, f, indent=2)
                self.logger.info(f"Version info saved to {self.env_settings['model_version_file']}")

            return True
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise

    def load(self, custom_path=None):
        """
        Load models and feature extractor from disk.

        Args:
            custom_path: Optional custom path to load model from
        """
        load_path = custom_path or MODEL_PATH

        try:
            # Use the provided path directly
            model_file = load_path

            # Check if model file exists
            if not os.path.exists(model_file):
                # Try with _purpose_model.pkl suffix as fallback for backward compatibility
                legacy_file = f"{load_path}_purpose_model.pkl"
                if os.path.exists(legacy_file):
                    self.logger.info(f"Using legacy model file format: {legacy_file}")
                    model_file = legacy_file
                else:
                    self.logger.error(f"Model file not found: {model_file} or {legacy_file}")
                    raise FileNotFoundError(f"Model file not found: {model_file} or {legacy_file}")

            # Load the model package
            self.logger.info(f"Loading model from {model_file}")
            model_package = joblib.load(model_file)

            # Check if the loaded object is a dictionary (model package)
            if not isinstance(model_package, dict):
                self.logger.error(f"Invalid model format: expected dictionary, got {type(model_package)}")
                raise ValueError(f"Invalid model format: expected dictionary, got {type(model_package)}")

            # Debug print of model package keys to help diagnose issues
            self.logger.debug(f"Model package keys: {list(model_package.keys())}")

            # Extract model components
            self.purpose_model = model_package.get('purpose_model')
            if self.purpose_model is None:
                raise ValueError("Model package does not contain a purpose model")

            self.category_purpose_model = model_package.get('category_purpose_model')
            self.feature_extractor = model_package.get('feature_extractor')
            if self.feature_extractor is None:
                raise ValueError("Model package does not contain a feature extractor")

            self.frequent_purpose_codes = model_package.get('frequent_purpose_codes', {})
            self.fallback_strategy = model_package.get('fallback_strategy', self.fallback_strategy)
            self.fallback_default = model_package.get('fallback_default', self.fallback_default)
            self.model_version = model_package.get('version', {})

            # Check if tech enhancer was used
            self.use_tech_enhancer = model_package.get('use_tech_enhancer', False)
            self.auto_tech_enhance = model_package.get('auto_tech_enhance', False)

            # Check if education enhancer was used
            self.use_education_enhancer = model_package.get('use_education_enhancer', False)
            self.auto_education_enhance = model_package.get('auto_education_enhance', False)

            # Initialize tech enhancer if needed
            if (self.use_tech_enhancer or self.auto_tech_enhance) and not hasattr(self, 'tech_enhancer'):
                self.tech_enhancer = TechDomainEnhancer()
                self.logger.info("Tech domain enhancer initialized from loaded model config")

            # Initialize education enhancer if needed
            if (self.use_education_enhancer or self.auto_education_enhance) and not hasattr(self, 'education_enhancer'):
                self.education_enhancer = EducationDomainEnhancer()
                self.logger.info("Education domain enhancer initialized from loaded model config")

            # Initialize category purpose enhancer if needed
            if (self.use_category_purpose_enhancer or self.auto_category_purpose_enhance) and not hasattr(self, 'category_purpose_enhancer'):
                self.category_purpose_enhancer = CategoryPurposeDomainEnhancer()
                self.logger.info("Category Purpose domain enhancer initialized from loaded model config")

            # Initialize transportation enhancer if needed
            if (self.use_transportation_enhancer or self.auto_transportation_enhance) and not hasattr(self, 'transportation_enhancer'):
                self.transportation_enhancer = TransportationDomainEnhancer()
                self.logger.info("Transportation domain enhancer initialized from loaded model config")

            # Initialize financial services enhancer if needed
            if (self.use_financial_services_enhancer or self.auto_financial_services_enhance) and not hasattr(self, 'financial_services_enhancer'):
                self.financial_services_enhancer = FinancialServicesDomainEnhancer()
                self.logger.info("Financial Services domain enhancer initialized from loaded model config")

            # Detect if model was trained with ensemble
            self.use_ensemble = isinstance(self.purpose_model, VotingClassifier)

            self.logger.info(f"Model loaded from {model_file} (version: {self.model_version})")

            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise