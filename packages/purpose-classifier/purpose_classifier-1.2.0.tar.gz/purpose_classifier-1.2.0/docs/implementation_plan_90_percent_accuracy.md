# Implementation Plan: Achieving 90% Accuracy with Semantic Pattern Matching

This document outlines the step-by-step implementation plan to improve the purpose code classification accuracy to 90% using semantic pattern matching approaches.

## Phase 1: Foundation - Semantic Pattern Matching Framework

- [ ] **1.1 Create SemanticPatternMatcher Base Class**
  - [ ] Implement word embedding loading functionality
    ```python
    def load_word_embeddings(self, model_path='models/word_embeddings.pkl'):
        """
        Load pre-trained word embeddings from file.
        Supports Word2Vec, GloVe, or FastText formats.
        """
        if model_path.endswith('.pkl'):
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        elif model_path.endswith('.bin'):
            return KeyedVectors.load_word2vec_format(model_path, binary=True)
        else:
            return KeyedVectors.load_word2vec_format(model_path)
    ```
  - [ ] Add semantic similarity calculation methods
    ```python
    def semantic_similarity(self, word1, word2, threshold=0.7):
        """
        Calculate semantic similarity between two words using word embeddings.
        Returns similarity score between 0 and 1.
        """
        if word1 not in self.embeddings or word2 not in self.embeddings:
            return 0.0

        similarity = self.embeddings.similarity(word1, word2)
        return max(0.0, min(1.0, (similarity + 1) / 2))  # Normalize to [0,1]

    def find_similar_words(self, word, threshold=0.7):
        """
        Find words semantically similar to the input word.
        Returns list of (word, similarity) tuples above threshold.
        """
        if word not in self.embeddings:
            return []

        similar_words = self.embeddings.most_similar(word, topn=20)
        return [(w, s) for w, s in similar_words if s >= threshold]
    ```
  - [ ] Create context matching algorithms
    ```python
    def context_match(self, text, context_patterns):
        """
        Match text against semantic context patterns.

        Args:
            text (str): The text to analyze
            context_patterns (list): List of context pattern dictionaries
                Each dict has keys: 'keywords', 'proximity', 'weight'

        Returns:
            float: Match score between 0 and 1
        """
        words = self.tokenize(text.lower())
        total_score = 0.0
        max_weight = sum(pattern['weight'] for pattern in context_patterns)

        for pattern in context_patterns:
            keywords = pattern['keywords']
            proximity = pattern['proximity']
            weight = pattern['weight']

            # Check if all keywords are within proximity
            if self.keywords_in_proximity(words, keywords, proximity):
                total_score += weight

        return total_score / max_weight if max_weight > 0 else 0.0
    ```
  - [ ] Add proximity-based pattern matching
    ```python
    def keywords_in_proximity(self, words, keywords, max_distance):
        """
        Check if all keywords appear within the specified proximity.

        Args:
            words (list): Tokenized words from text
            keywords (list): Keywords to check for
            max_distance (int): Maximum word distance between keywords

        Returns:
            bool: True if all keywords are within proximity
        """
        # Find positions of all keywords
        positions = {}
        for keyword in keywords:
            keyword_positions = []
            for i, word in enumerate(words):
                if word == keyword or self.semantic_similarity(word, keyword) > 0.8:
                    keyword_positions.append(i)
            if not keyword_positions:
                return False
            positions[keyword] = keyword_positions

        # Check if any combination of positions is within max_distance
        position_combinations = itertools.product(*positions.values())
        for combo in position_combinations:
            if max(combo) - min(combo) <= max_distance:
                return True

        return False
    ```
  - [ ] Implement confidence scoring mechanisms
    ```python
    def calculate_confidence(self, match_scores, weights=None):
        """
        Calculate overall confidence score from multiple match scores.

        Args:
            match_scores (dict): Dictionary of {pattern_name: score}
            weights (dict, optional): Dictionary of {pattern_name: weight}

        Returns:
            float: Confidence score between 0 and 1
        """
        if not match_scores:
            return 0.0

        if weights is None:
            weights = {name: 1.0 for name in match_scores}

        total_weight = sum(weights.values())
        weighted_score = sum(score * weights.get(name, 1.0)
                            for name, score in match_scores.items())

        return weighted_score / total_weight if total_weight > 0 else 0.0
    ```

- [ ] **1.2 Set Up Testing Framework**
  - [ ] Create additional test cases for problematic purpose codes
    ```python
    # tests/test_semantic_enhancers.py

    def create_test_cases_for_problematic_codes():
        """Generate comprehensive test cases for problematic purpose codes."""
        test_cases = []

        # Dividend test cases
        dividend_test_cases = [
            {"narration": "Dividend payment Q2 2023", "expected": "DIVD", "message_type": "MT103"},
            {"narration": "Shareholder dividend final 2023", "expected": "DIVD", "message_type": "MT103"},
            {"narration": "Quarterly dividend distribution", "expected": "DIVD", "message_type": "MT202"},
            {"narration": "Interim dividend payout", "expected": "DIVD", "message_type": "MT202COV"},
            {"narration": "Corporate dividend Q1 2023", "expected": "DIVD", "message_type": "MT205"},
            # Add more dividend test cases with variations
        ]
        test_cases.extend(dividend_test_cases)

        # Loan/Loan Repayment test cases
        loan_test_cases = [
            {"narration": "Loan disbursement - Account ID123456", "expected": "LOAN", "message_type": "MT103"},
            {"narration": "New loan facility - REF123456", "expected": "LOAN", "message_type": "MT103"},
            {"narration": "Loan repayment - Account ID123456", "expected": "LOAR", "message_type": "MT103"},
            {"narration": "Monthly loan installment", "expected": "LOAR", "message_type": "MT202"},
            # Add more loan test cases with variations
        ]
        test_cases.extend(loan_test_cases)

        # Add test cases for other problematic codes (TRAD, etc.)

        return test_cases
    ```
  - [ ] Implement cross-validation for enhancer evaluation
    ```python
    # tests/test_enhancer_evaluation.py

    def evaluate_enhancer_with_cross_validation(enhancer_class, test_data, k=5):
        """
        Evaluate enhancer performance using k-fold cross-validation.

        Args:
            enhancer_class: The enhancer class to evaluate
            test_data: List of test cases
            k: Number of folds for cross-validation

        Returns:
            dict: Performance metrics
        """
        # Split data into k folds
        folds = np.array_split(test_data, k)
        metrics = {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1': []
        }

        # Perform k-fold cross-validation
        for i in range(k):
            # Use fold i as test set, rest as training
            test_fold = folds[i]
            train_folds = [fold for j, fold in enumerate(folds) if j != i]
            train_data = [item for fold in train_folds for item in fold]

            # Train enhancer on training data (if applicable)
            enhancer = enhancer_class()
            if hasattr(enhancer, 'train'):
                enhancer.train(train_data)

            # Test enhancer on test fold
            results = []
            for case in test_fold:
                result = {'purpose_code': 'OTHR', 'confidence': 0.3}
                enhanced_result = enhancer.enhance_classification(
                    result, case['narration'], case.get('message_type')
                )
                results.append({
                    'expected': case['expected'],
                    'predicted': enhanced_result['purpose_code'],
                    'confidence': enhanced_result['confidence']
                })

            # Calculate metrics for this fold
            fold_metrics = calculate_metrics(results)
            for metric, value in fold_metrics.items():
                metrics[metric].append(value)

        # Average metrics across folds
        return {metric: np.mean(values) for metric, values in metrics.items()}
    ```
  - [ ] Add metrics tracking (accuracy, precision, recall, F1-score)
    ```python
    # utils/metrics.py

    def calculate_metrics(results):
        """
        Calculate performance metrics for classification results.

        Args:
            results: List of dictionaries with 'expected' and 'predicted' keys

        Returns:
            dict: Performance metrics
        """
        # Extract expected and predicted labels
        y_true = [r['expected'] for r in results]
        y_pred = [r['predicted'] for r in results]

        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        # Calculate per-class metrics
        class_report = classification_report(y_true, y_pred, output_dict=True)

        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'class_report': class_report,
            'confusion_matrix': cm
        }
    ```
  - [ ] Create visualization tools for error analysis
    ```python
    # utils/visualization.py

    def plot_confusion_matrix(cm, classes, title='Confusion Matrix'):
        """
        Plot confusion matrix as a heatmap.

        Args:
            cm: Confusion matrix
            classes: List of class names
            title: Plot title
        """
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=classes, yticklabels=classes)
        plt.title(title)
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png')
        plt.close()

    def plot_error_distribution(results):
        """
        Plot distribution of errors by purpose code.

        Args:
            results: List of dictionaries with 'expected' and 'predicted' keys
        """
        # Filter for errors
        errors = [r for r in results if r['expected'] != r['predicted']]

        # Count errors by expected class
        error_counts = Counter([e['expected'] for e in errors])

        # Plot
        plt.figure(figsize=(12, 6))
        sns.barplot(x=list(error_counts.keys()), y=list(error_counts.values()))
        plt.title('Error Distribution by Purpose Code')
        plt.xlabel('Purpose Code')
        plt.ylabel('Error Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('error_distribution.png')
        plt.close()
    ```

- [ ] **1.3 Enhancer Manager Improvements**
  - [ ] Refine enhancer priority system
    ```python
    # purpose_classifier/domain_enhancers/enhancer_manager.py

    class EnhancerManager:
        def __init__(self):
            # Initialize all enhancers
            self.enhancers = {
                # Highest priority enhancers (semantic pattern matchers)
                'dividend': DividendEnhancer(),  # New dedicated enhancer
                'pattern': PatternEnhancer(),    # Enhanced with semantic patterns

                # High-priority enhancers
                'property_purchase': PropertyPurchaseEnhancer(),
                'card_payment': CardPaymentEnhancer(),
                'loan': LoanEnhancer(),          # New dedicated enhancer
                'investment': InvestmentEnhancer(),
                'trade': TradeEnhancer(),        # Enhanced with semantic patterns

                # Medium-priority enhancers
                'education': EducationDomainEnhancer(),
                'services': ServicesDomainEnhancer(),
                'goods': GoodsDomainEnhancer(),
                'insurance': InsuranceDomainEnhancer(),

                # Low-priority enhancers
                'message_type': MessageTypeContextEnhancer(),  # New context-aware enhancer
                'category_purpose': CategoryPurposeEnhancer(),
            }

            # Define enhancer priorities with weights
            self.priorities = {
                'dividend': {'level': 'highest', 'weight': 1.0},
                'pattern': {'level': 'highest', 'weight': 0.9},
                'property_purchase': {'level': 'high', 'weight': 0.8},
                'card_payment': {'level': 'high', 'weight': 0.8},
                'loan': {'level': 'high', 'weight': 0.8},
                'investment': {'level': 'high', 'weight': 0.8},
                'trade': {'level': 'high', 'weight': 0.8},
                'education': {'level': 'medium', 'weight': 0.7},
                'services': {'level': 'medium', 'weight': 0.7},
                'goods': {'level': 'medium', 'weight': 0.7},
                'insurance': {'level': 'medium', 'weight': 0.7},
                'message_type': {'level': 'low', 'weight': 0.6},
                'category_purpose': {'level': 'low', 'weight': 0.5},
            }
    ```
  - [ ] Implement confidence threshold overrides
    ```python
    def enhance_classification(self, result, narration, message_type=None):
        """
        Apply all enhancers to improve classification result.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        original_result = result.copy()
        current_result = result.copy()

        # Track enhancer decisions for logging
        enhancer_decisions = []

        # Apply enhancers in priority order
        for level in ['highest', 'high', 'medium', 'low']:
            level_enhancers = [name for name, config in self.priorities.items()
                              if config['level'] == level]

            for enhancer_name in level_enhancers:
                enhancer = self.enhancers[enhancer_name]

                # Apply enhancer
                enhanced = enhancer.enhance_classification(
                    current_result.copy(), narration, message_type
                )

                # Check if enhancer changed the result
                if enhanced['purpose_code'] != current_result['purpose_code']:
                    # Calculate confidence threshold based on priority weight
                    priority_weight = self.priorities[enhancer_name]['weight']
                    confidence_threshold = 0.5 + (0.3 * priority_weight)

                    # Apply confidence threshold override
                    if enhanced['confidence'] >= confidence_threshold:
                        # Record decision for logging
                        enhancer_decisions.append({
                            'enhancer': enhancer_name,
                            'old_code': current_result['purpose_code'],
                            'new_code': enhanced['purpose_code'],
                            'confidence': enhanced['confidence'],
                            'threshold': confidence_threshold,
                            'applied': True
                        })

                        # Update current result
                        current_result = enhanced
                    else:
                        # Record decision for logging (not applied)
                        enhancer_decisions.append({
                            'enhancer': enhancer_name,
                            'old_code': current_result['purpose_code'],
                            'new_code': enhanced['purpose_code'],
                            'confidence': enhanced['confidence'],
                            'threshold': confidence_threshold,
                            'applied': False
                        })

        # Add enhancer decisions to result for logging
        current_result['enhancer_decisions'] = enhancer_decisions

        return current_result
    ```
  - [ ] Add context-aware enhancer selection
    ```python
    def select_enhancers_by_context(self, narration, message_type=None):
        """
        Select relevant enhancers based on context.

        Args:
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            list: Names of relevant enhancers
        """
        narration_lower = narration.lower()
        relevant_enhancers = []

        # Check for dividend context
        if any(term in narration_lower for term in ['dividend', 'shareholder']):
            relevant_enhancers.append('dividend')

        # Check for loan context
        if any(term in narration_lower for term in ['loan', 'credit', 'facility']):
            relevant_enhancers.append('loan')

        # Check for investment context
        if any(term in narration_lower for term in ['invest', 'securities', 'shares']):
            relevant_enhancers.append('investment')

        # Check for trade context
        if any(term in narration_lower for term in ['trade', 'import', 'export']):
            relevant_enhancers.append('trade')

        # Add message type enhancer if message type is provided
        if message_type:
            relevant_enhancers.append('message_type')

        # Always include pattern enhancer and category purpose enhancer
        relevant_enhancers.extend(['pattern', 'category_purpose'])

        # Remove duplicates while preserving order
        return list(dict.fromkeys(relevant_enhancers))
    ```
  - [ ] Create logging for enhancer decision process
    ```python
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
        logger.debug(f"Initial purpose code: {result.get('initial_purpose_code', 'OTHR')}")
        logger.debug(f"Final purpose code: {result['purpose_code']}")

        for decision in decisions:
            applied_str = "APPLIED" if decision['applied'] else "NOT APPLIED"
            logger.debug(
                f"Enhancer: {decision['enhancer']} | "
                f"{decision['old_code']} -> {decision['new_code']} | "
                f"Confidence: {decision['confidence']:.2f} | "
                f"Threshold: {decision['threshold']:.2f} | "
                f"{applied_str}"
            )
    ```

## Phase 2: Specialized Enhancers for Problematic Codes

- [ ] **2.0 Enhancer Base Class Refactoring**
  - [ ] Create a new `SemanticEnhancer` base class
    ```python
    # purpose_classifier/domain_enhancers/semantic_enhancer.py

    from purpose_classifier.domain_enhancers.base_enhancer import BaseEnhancer
    from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher
    import logging

    logger = logging.getLogger(__name__)

    class SemanticEnhancer(BaseEnhancer, SemanticPatternMatcher):
        """
        Base class for all semantic enhancers.
        Combines BaseEnhancer functionality with semantic pattern matching.
        """

        def __init__(self):
            BaseEnhancer.__init__(self)
            SemanticPatternMatcher.__init__(self)

            # Initialize common patterns and contexts
            self.context_patterns = []
            self.direct_keywords = {}
            self.semantic_terms = []
            self.confidence_thresholds = {
                'direct_match': 0.95,
                'context_match': 0.85,
                'semantic_match': 0.75
            }

        def enhance_classification(self, result, narration, message_type=None):
            """
            Base implementation of semantic enhancement.

            Args:
                result: Initial classification result
                narration: Transaction narration
                message_type: Optional message type

            Returns:
                dict: Enhanced classification result
            """
            # Subclasses should override this method
            return result

        def direct_keyword_match(self, narration, purpose_code):
            """
            Check for direct keyword matches.

            Args:
                narration: Transaction narration
                purpose_code: Purpose code to check keywords for

            Returns:
                tuple: (matched, confidence, keyword)
            """
            narration_lower = narration.lower()

            if purpose_code not in self.direct_keywords:
                return (False, 0.0, None)

            for keyword in self.direct_keywords[purpose_code]:
                if keyword in narration_lower:
                    return (True, self.confidence_thresholds['direct_match'], keyword)

            return (False, 0.0, None)

        def context_match(self, narration, purpose_code):
            """
            Check for context pattern matches.

            Args:
                narration: Transaction narration
                purpose_code: Purpose code to check context for

            Returns:
                tuple: (matched, confidence, pattern)
            """
            narration_lower = narration.lower()

            # Filter context patterns for this purpose code
            relevant_patterns = [p for p in self.context_patterns
                               if p.get('purpose_code') == purpose_code]

            if not relevant_patterns:
                return (False, 0.0, None)

            # Check each pattern
            for pattern in relevant_patterns:
                keywords = pattern['keywords']
                proximity = pattern['proximity']
                weight = pattern['weight']

                if self.keywords_in_proximity(self.tokenize(narration_lower),
                                           keywords, proximity):
                    confidence = min(self.confidence_thresholds['context_match'],
                                   weight)
                    return (True, confidence, pattern)

            return (False, 0.0, None)

        def semantic_similarity_match(self, narration, purpose_code):
            """
            Check for semantic similarity matches.

            Args:
                narration: Transaction narration
                purpose_code: Purpose code to check semantic similarity for

            Returns:
                tuple: (matched, confidence, matches)
            """
            narration_lower = narration.lower()
            words = self.tokenize(narration_lower)

            # Filter semantic terms for this purpose code
            relevant_terms = [t for t in self.semantic_terms
                            if t.get('purpose_code') == purpose_code]

            if not relevant_terms:
                return (False, 0.0, [])

            # Check semantic similarity
            matches = []
            for term_data in relevant_terms:
                term = term_data['term']
                threshold = term_data.get('threshold', 0.7)
                weight = term_data.get('weight', 1.0)

                for word in words:
                    similarity = self.semantic_similarity(word, term)
                    if similarity >= threshold:
                        matches.append((word, term, similarity, weight))

            if matches:
                # Calculate weighted average similarity
                total_weight = sum(m[3] for m in matches)
                weighted_similarity = sum(m[2] * m[3] for m in matches) / total_weight
                confidence = min(self.confidence_thresholds['semantic_match'],
                               weighted_similarity)
                return (True, confidence, matches)

            return (False, 0.0, [])
    ```
  - [ ] Update all enhancers to inherit from `SemanticEnhancer`
  - [ ] Create migration script to convert existing enhancers
    ```python
    # scripts/migrate_enhancers_to_semantic.py

    import os
    import re
    import glob

    def migrate_enhancer(file_path):
        """Migrate an existing enhancer to use the semantic approach."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Update imports
        content = re.sub(
            r'from purpose_classifier\.domain_enhancers\.base_enhancer import BaseEnhancer',
            'from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer',
            content
        )

        # Update class definition
        content = re.sub(
            r'class (\w+)\(BaseEnhancer\):',
            r'class \1(SemanticEnhancer):',
            content
        )

        # Update __init__ method
        init_pattern = re.compile(r'def __init__\(self\):(.*?)def', re.DOTALL)
        if init_match := init_pattern.search(content):
            init_content = init_match.group(1)
            new_init = f"""def __init__(self):
        SemanticEnhancer.__init__(self)

        # Initialize patterns and contexts
        self._initialize_patterns()

    def _initialize_patterns(self):
        \"\"\"Initialize semantic patterns and contexts.\"\"\"
        # Direct keywords with purpose codes
        self.direct_keywords = {self._extract_keywords(init_content)}

        # Semantic context patterns
        self.context_patterns = []

        # Semantic terms for similarity matching
        self.semantic_terms = []

    def"""
            content = init_pattern.sub(new_init, content)

        # Save updated file
        with open(file_path, 'w') as f:
            f.write(content)

    def _extract_keywords(init_content):
        """Extract keywords from existing enhancer init method."""
        # Implementation depends on the structure of existing enhancers
        # This is a placeholder
        return "{}"

    def migrate_all_enhancers():
        """Migrate all existing enhancers to use the semantic approach."""
        enhancer_files = glob.glob('purpose_classifier/domain_enhancers/*_enhancer.py')
        for file_path in enhancer_files:
            if 'base_enhancer.py' not in file_path and 'semantic_enhancer.py' not in file_path:
                print(f"Migrating {file_path}...")
                migrate_enhancer(file_path)

    if __name__ == '__main__':
        migrate_all_enhancers()
    ```

- [ ] **2.1 Dividend Enhancer (DIVD) - Priority 1**
  - [ ] Create dedicated DividendEnhancer class
    ```python
    # purpose_classifier/domain_enhancers/dividend_enhancer.py

    from purpose_classifier.domain_enhancers.base_enhancer import BaseEnhancer
    from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher
    import logging

    logger = logging.getLogger(__name__)

    class DividendEnhancer(BaseEnhancer, SemanticPatternMatcher):
        """
        Specialized enhancer for dividend payments.
        Uses semantic pattern matching to identify dividend-related transactions.
        """

        def __init__(self):
            BaseEnhancer.__init__(self)
            SemanticPatternMatcher.__init__(self)

            # Initialize dividend-specific patterns and contexts
            self._initialize_patterns()

        def _initialize_patterns(self):
            """Initialize dividend-specific patterns and contexts."""
            # Direct dividend keywords (highest confidence)
            self.dividend_keywords = [
                'dividend', 'dividends', 'div', 'div.', 'dividend payment',
                'shareholder dividend', 'shareholder distribution',
                'dividend distribution', 'dividend payout',
                'quarterly dividend', 'annual dividend', 'interim dividend',
                'final dividend', 'special dividend', 'cash dividend',
                'stock dividend', 'share dividend', 'dividend income'
            ]

            # Semantic context patterns for dividends
            self.dividend_contexts = [
                {"keywords": ["dividend", "payment"], "proximity": 5, "weight": 1.0},
                {"keywords": ["shareholder", "dividend"], "proximity": 3, "weight": 1.0},
                {"keywords": ["quarterly", "dividend"], "proximity": 3, "weight": 0.9},
                {"keywords": ["interim", "dividend"], "proximity": 3, "weight": 0.9},
                {"keywords": ["final", "dividend"], "proximity": 3, "weight": 0.9},
                {"keywords": ["annual", "dividend"], "proximity": 3, "weight": 0.9},
                {"keywords": ["dividend", "distribution"], "proximity": 5, "weight": 0.8},
                {"keywords": ["dividend", "payout"], "proximity": 5, "weight": 0.8},
                {"keywords": ["profit", "sharing"], "proximity": 3, "weight": 0.7},
                {"keywords": ["profit", "distribution"], "proximity": 3, "weight": 0.7},
                {"keywords": ["shareholder", "payout"], "proximity": 3, "weight": 0.8},
                {"keywords": ["shareholder", "distribution"], "proximity": 3, "weight": 0.8}
            ]

            # Dividend-related terms for semantic similarity matching
            self.dividend_related_terms = [
                'dividend', 'shareholder', 'payout', 'distribution', 'quarterly',
                'annual', 'interim', 'final', 'profit', 'sharing', 'earnings'
            ]
    ```
  - [ ] Implement semantic context patterns for dividends
    ```python
    def enhance_classification(self, result, narration, message_type=None):
        """
        Enhance classification for dividend payments.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        """
        # Don't override if already classified as DIVD with high confidence
        if result['purpose_code'] == 'DIVD' and result['confidence'] >= 0.8:
            return result

        narration_lower = narration.lower()

        # Direct keyword matching (highest confidence)
        for keyword in self.dividend_keywords:
            if keyword in narration_lower:
                logger.debug(f"Dividend keyword match: {keyword}")
                return {
                    'purpose_code': 'DIVD',
                    'confidence': 0.99,
                    'category_purpose_code': 'DIVD',
                    'enhancer': 'dividend_enhancer',
                    'reason': f"Direct dividend keyword match: {keyword}"
                }

        # Semantic context pattern matching
        context_score = self.context_match(narration_lower, self.dividend_contexts)
        if context_score >= 0.7:
            logger.debug(f"Dividend context match with score: {context_score:.2f}")
            return {
                'purpose_code': 'DIVD',
                'confidence': min(0.95, context_score),
                'category_purpose_code': 'DIVD',
                'enhancer': 'dividend_enhancer',
                'reason': f"Dividend context match with score: {context_score:.2f}"
            }

        # Check for semantic similarity with dividend-related terms
        semantic_matches = []
        words = self.tokenize(narration_lower)

        for word in words:
            for term in self.dividend_related_terms:
                similarity = self.semantic_similarity(word, term)
                if similarity >= 0.8:
                    semantic_matches.append((word, term, similarity))

        # If we have multiple semantic matches, likely a dividend
        if len(semantic_matches) >= 2:
            avg_similarity = sum(m[2] for m in semantic_matches) / len(semantic_matches)
            logger.debug(f"Dividend semantic matches: {semantic_matches}")
            return {
                'purpose_code': 'DIVD',
                'confidence': min(0.9, avg_similarity),
                'category_purpose_code': 'DIVD',
                'enhancer': 'dividend_enhancer',
                'reason': f"Semantic similarity matches: {len(semantic_matches)}"
            }

        # No dividend pattern detected
        return result
    ```
  - [ ] Add word embedding-based similarity for dividend terms
    ```python
    def semantic_dividend_detection(self, narration):
        """
        Detect dividend payments using word embeddings and semantic similarity.

        Args:
            narration: Transaction narration

        Returns:
            tuple: (is_dividend, confidence, reason)
        """
        narration_lower = narration.lower()
        words = self.tokenize(narration_lower)

        # Find words semantically similar to 'dividend'
        dividend_similarities = []
        for word in words:
            similarity = self.semantic_similarity(word, 'dividend')
            if similarity >= 0.7:
                dividend_similarities.append((word, similarity))

        # Find words semantically similar to 'shareholder'
        shareholder_similarities = []
        for word in words:
            similarity = self.semantic_similarity(word, 'shareholder')
            if similarity >= 0.7:
                shareholder_similarities.append((word, similarity))

        # Calculate overall dividend confidence
        if dividend_similarities:
            max_dividend_sim = max(s[1] for s in dividend_similarities)
            max_shareholder_sim = max(s[1] for s in shareholder_similarities) if shareholder_similarities else 0

            # Combine similarities with higher weight for dividend
            combined_confidence = (0.7 * max_dividend_sim) + (0.3 * max_shareholder_sim)

            if combined_confidence >= 0.7:
                return (True, combined_confidence, f"Semantic similarity: dividend={max_dividend_sim:.2f}, shareholder={max_shareholder_sim:.2f}")

        return (False, 0.0, "No semantic dividend pattern detected")
    ```
  - [ ] Implement confidence threshold override for dividend terms
    ```python
    def should_override_classification(self, result, narration):
        """
        Determine if dividend classification should override existing classification.

        Args:
            result: Current classification result
            narration: Transaction narration

        Returns:
            bool: True if should override
        """
        narration_lower = narration.lower()

        # Always override if direct dividend keyword is present
        for keyword in self.dividend_keywords:
            if keyword in narration_lower:
                return True

        # Check for strong dividend context
        context_score = self.context_match(narration_lower, self.dividend_contexts)
        if context_score >= 0.8:
            return True

        # Check if current classification is investment-related
        if result['purpose_code'] == 'INVS' and context_score >= 0.6:
            # Override investment classification with medium confidence
            return True

        # Don't override other classifications unless very strong evidence
        return False
    ```
  - [ ] Add special handling for dividend-related keywords
    ```python
    def handle_edge_cases(self, narration):
        """
        Handle special edge cases for dividend classification.

        Args:
            narration: Transaction narration

        Returns:
            tuple: (is_dividend, confidence, reason)
        """
        narration_lower = narration.lower()

        # Handle profit sharing (semantically similar to dividends)
        if 'profit sharing' in narration_lower or 'profit distribution' in narration_lower:
            return (True, 0.9, "Profit sharing is semantically equivalent to dividends")

        # Handle stock dividends
        if ('stock' in narration_lower and 'dividend' in narration_lower) or 'stock dividend' in narration_lower:
            return (True, 0.95, "Stock dividend explicitly mentioned")

        # Handle dividend reinvestment plans (DRIPs)
        if 'drip' in narration_lower or 'dividend reinvestment' in narration_lower:
            return (True, 0.95, "Dividend reinvestment plan (DRIP)")

        # Handle dividend income
        if 'dividend income' in narration_lower:
            return (True, 0.95, "Dividend income explicitly mentioned")

        # Not a special case
        return (False, 0.0, "No special dividend case detected")
    ```
  - [ ] Test with dividend-specific test cases
    ```python
    # tests/test_dividend_enhancer.py

    import unittest
    from purpose_classifier.domain_enhancers.dividend_enhancer import DividendEnhancer

    class TestDividendEnhancer(unittest.TestCase):
        def setUp(self):
            self.enhancer = DividendEnhancer()

        def test_direct_keyword_matching(self):
            # Test direct keyword matching
            test_cases = [
                "Dividend payment for Q2 2023",
                "Shareholder dividend final 2023",
                "Quarterly dividend distribution",
                "Interim dividend payout",
                "Corporate dividend Q1 2023"
            ]

            for narration in test_cases:
                result = {'purpose_code': 'OTHR', 'confidence': 0.3}
                enhanced = self.enhancer.enhance_classification(result, narration)
                self.assertEqual(enhanced['purpose_code'], 'DIVD')
                self.assertGreaterEqual(enhanced['confidence'], 0.9)

        def test_semantic_context_matching(self):
            # Test semantic context matching
            test_cases = [
                "Payment of shareholder profits for Q2",
                "Distribution of quarterly profits to shareholders",
                "Annual profit sharing payment",
                "Company earnings distribution for shareholders"
            ]

            for narration in test_cases:
                result = {'purpose_code': 'OTHR', 'confidence': 0.3}
                enhanced = self.enhancer.enhance_classification(result, narration)
                self.assertEqual(enhanced['purpose_code'], 'DIVD')
                self.assertGreaterEqual(enhanced['confidence'], 0.7)

        def test_override_investment_classification(self):
            # Test overriding investment classification
            test_cases = [
                "Dividend payment for investment portfolio",
                "Shareholder dividend from stock investments",
                "Quarterly dividend from securities"
            ]

            for narration in test_cases:
                result = {'purpose_code': 'INVS', 'confidence': 0.8}
                enhanced = self.enhancer.enhance_classification(result, narration)
                self.assertEqual(enhanced['purpose_code'], 'DIVD')
                self.assertGreaterEqual(enhanced['confidence'], 0.9)
    ```

- [ ] **2.2 Loan/Loan Repayment Enhancer (LOAN/LOAR) - Priority 2**
  - [ ] Create dedicated LoanEnhancer class
  - [ ] Implement semantic context patterns for loans vs. repayments
  - [ ] Add directional analysis (money flow direction)
  - [ ] Implement temporal understanding for repayment schedules
  - [ ] Add semantic similarity for loan types
  - [ ] Test with loan-specific test cases

- [ ] **2.3 Trade Enhancer (TRAD) - Priority 3**
  - [ ] Enhance existing TradeEnhancer
  - [ ] Implement semantic context patterns for trade
  - [ ] Add cross-border detection mechanisms
  - [ ] Implement semantic similarity for trade-related terms
  - [ ] Add special handling for international vs. domestic transactions
  - [ ] Test with trade-specific test cases

## Phase 3: Message Type Context Awareness (Completed)

- [x] **3.1 Context-Aware Message Type Enhancer**
  - [x] Create MessageTypeContextEnhancer class
  - [x] Implement context patterns for each message type
  - [x] Add semantic understanding of message type purposes
  - [x] Implement fallback strategies based on message type and narration
  - [x] Test with message-type-specific test cases

- [x] **3.2 MT202/MT202COV Specific Improvements**
  - [x] Create dedicated MT202Enhancer class
  - [x] Implement semantic context patterns for MT202/MT202COV
  - [x] Add interbank transaction detection
  - [x] Implement securities settlement recognition
  - [x] Add treasury operation detection
  - [x] Test with MT202/MT202COV-specific test cases

### Implementation Details:

1. **MessageTypeContextEnhancer**
   - Created a dedicated enhancer that uses message type context
   - Implemented direct keyword matching for message type specific purpose codes
   - Added context patterns for each message type
   - Implemented confidence adjustment based on message type preferences
   - Added fallback strategies for ambiguous narrations

2. **MT202Enhancer**
   - Created a specialized enhancer for MT202 and MT202COV messages
   - Implemented semantic context patterns for interbank transfers, treasury operations, and securities settlement
   - Added interbank transaction detection with pattern matching
   - Implemented securities settlement recognition
   - Added treasury operation detection
   - Added direct mapping of category purpose codes

3. **Integration with EnhancerManager**
   - Updated the EnhancerManager to include the new enhancers
   - Added context-aware enhancer selection based on message type
   - Set appropriate priorities for the new enhancers

### Outcome:
- Improved classification accuracy for MT202 and MT202COV messages
- Better handling of ambiguous narrations based on message type
- Reduced OTHR usage for interbank transfers
- Enhanced category purpose code mapping for MT202 and MT202COV messages

## Phase 4: Category Purpose Code Mapping

- [ ] **4.1 Comprehensive Mapping System**
  - [ ] Create CategoryPurposeMapper class
  - [ ] Implement direct mapping with semantic context awareness
  - [ ] Add purpose code to category purpose code mapping functions
  - [ ] Implement fallback strategies for category purpose codes
  - [ ] Test with category-purpose-specific test cases

- [ ] **4.2 Category Purpose Enhancer**
  - [ ] Enhance existing CategoryPurposeEnhancer
  - [ ] Integrate with CategoryPurposeMapper
  - [ ] Add semantic context understanding for category determination
  - [ ] Implement confidence scoring for category purpose codes
  - [ ] Test with comprehensive test cases

## Phase 5: Revamping Existing Enhancers

- [ ] **5.1 Create Semantic Enhancer Base Class**
  - [ ] Implement `SemanticEnhancer` base class
    ```python
    # purpose_classifier/domain_enhancers/semantic_enhancer.py

    from purpose_classifier.domain_enhancers.base_enhancer import BaseEnhancer
    from purpose_classifier.semantic_pattern_matcher import SemanticPatternMatcher
    import logging

    logger = logging.getLogger(__name__)

    class SemanticEnhancer(BaseEnhancer, SemanticPatternMatcher):
        """
        Base class for all semantic enhancers.
        Combines BaseEnhancer functionality with semantic pattern matching.
        """

        def __init__(self):
            BaseEnhancer.__init__(self)
            SemanticPatternMatcher.__init__(self)

            # Initialize common patterns and contexts
            self.context_patterns = []
            self.direct_keywords = {}
            self.semantic_terms = []
            self.confidence_thresholds = {
                'direct_match': 0.95,
                'context_match': 0.85,
                'semantic_match': 0.75
            }

        def enhance_classification(self, result, narration, message_type=None):
            """
            Base implementation of semantic enhancement.

            Args:
                result: Initial classification result
                narration: Transaction narration
                message_type: Optional message type

            Returns:
                dict: Enhanced classification result
            """
            narration_lower = narration.lower()

            # Check for direct keyword matches first (highest confidence)
            for purpose_code in self.direct_keywords:
                matched, confidence, keyword = self.direct_keyword_match(
                    narration_lower, purpose_code
                )
                if matched:
                    return {
                        'purpose_code': purpose_code,
                        'confidence': confidence,
                        'enhancer': self.__class__.__name__.lower(),
                        'reason': f"Direct keyword match: {keyword}"
                    }

            # Check for context pattern matches next
            for pattern in self.context_patterns:
                purpose_code = pattern.get('purpose_code')
                matched, confidence, pattern_info = self.context_match(
                    narration_lower, purpose_code
                )
                if matched:
                    return {
                        'purpose_code': purpose_code,
                        'confidence': confidence,
                        'enhancer': self.__class__.__name__.lower(),
                        'reason': f"Context pattern match: {pattern_info['keywords']}"
                    }

            # Check for semantic similarity matches last
            for term in self.semantic_terms:
                purpose_code = term.get('purpose_code')
                matched, confidence, matches = self.semantic_similarity_match(
                    narration_lower, purpose_code
                )
                if matched:
                    return {
                        'purpose_code': purpose_code,
                        'confidence': confidence,
                        'enhancer': self.__class__.__name__.lower(),
                        'reason': f"Semantic similarity match: {len(matches)} matches"
                    }

            # No matches found, return original result
            return result

        def direct_keyword_match(self, narration, purpose_code):
            """
            Check for direct keyword matches.

            Args:
                narration: Transaction narration
                purpose_code: Purpose code to check keywords for

            Returns:
                tuple: (matched, confidence, keyword)
            """
            if purpose_code not in self.direct_keywords:
                return (False, 0.0, None)

            for keyword in self.direct_keywords[purpose_code]:
                if keyword in narration:
                    return (True, self.confidence_thresholds['direct_match'], keyword)

            return (False, 0.0, None)

        def context_match(self, narration, purpose_code):
            """
            Check for context pattern matches.

            Args:
                narration: Transaction narration
                purpose_code: Purpose code to check context for

            Returns:
                tuple: (matched, confidence, pattern)
            """
            # Filter context patterns for this purpose code
            relevant_patterns = [p for p in self.context_patterns
                               if p.get('purpose_code') == purpose_code]

            if not relevant_patterns:
                return (False, 0.0, None)

            # Check each pattern
            for pattern in relevant_patterns:
                keywords = pattern['keywords']
                proximity = pattern['proximity']
                weight = pattern['weight']

                if self.keywords_in_proximity(self.tokenize(narration),
                                           keywords, proximity):
                    confidence = min(self.confidence_thresholds['context_match'],
                                   weight)
                    return (True, confidence, pattern)

            return (False, 0.0, None)

        def semantic_similarity_match(self, narration, purpose_code):
            """
            Check for semantic similarity matches.

            Args:
                narration: Transaction narration
                purpose_code: Purpose code to check semantic similarity for

            Returns:
                tuple: (matched, confidence, matches)
            """
            words = self.tokenize(narration)

            # Filter semantic terms for this purpose code
            relevant_terms = [t for t in self.semantic_terms
                            if t.get('purpose_code') == purpose_code]

            if not relevant_terms:
                return (False, 0.0, [])

            # Check semantic similarity
            matches = []
            for term_data in relevant_terms:
                term = term_data['term']
                threshold = term_data.get('threshold', 0.7)
                weight = term_data.get('weight', 1.0)

                for word in words:
                    similarity = self.semantic_similarity(word, term)
                    if similarity >= threshold:
                        matches.append((word, term, similarity, weight))

            if matches:
                # Calculate weighted average similarity
                total_weight = sum(m[3] for m in matches)
                weighted_similarity = sum(m[2] * m[3] for m in matches) / total_weight
                confidence = min(self.confidence_thresholds['semantic_match'],
                               weighted_similarity)
                return (True, confidence, matches)

            return (False, 0.0, [])
    ```
  - [ ] Create unit tests for `SemanticEnhancer` base class
  - [ ] Document the semantic enhancer approach

- [ ] **5.2 Revamp Domain-Specific Enhancers**
  - [ ] Update `EducationDomainEnhancer` to use semantic patterns
    ```python
    # purpose_classifier/domain_enhancers/education_domain_enhancer.py

    from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer
    import logging

    logger = logging.getLogger(__name__)

    class EducationDomainEnhancer(SemanticEnhancer):
        """
        Enhancer for education-related transactions.
        Uses semantic pattern matching to identify education payments.
        """

        def __init__(self):
            super().__init__()
            self._initialize_patterns()

        def _initialize_patterns(self):
            """Initialize education-specific patterns and contexts."""
            # Direct education keywords
            self.direct_keywords = {
                'EDUC': [
                    'tuition', 'school fee', 'college fee', 'university fee',
                    'education payment', 'student loan', 'school payment',
                    'course fee', 'education fee', 'academic fee',
                    'scholarship', 'bursary', 'student grant'
                ]
            }

            # Semantic context patterns for education
            self.context_patterns = [
                {
                    'purpose_code': 'EDUC',
                    'keywords': ['tuition', 'payment'],
                    'proximity': 5,
                    'weight': 0.9
                },
                {
                    'purpose_code': 'EDUC',
                    'keywords': ['school', 'fee'],
                    'proximity': 3,
                    'weight': 0.9
                },
                {
                    'purpose_code': 'EDUC',
                    'keywords': ['college', 'payment'],
                    'proximity': 5,
                    'weight': 0.9
                },
                {
                    'purpose_code': 'EDUC',
                    'keywords': ['university', 'fee'],
                    'proximity': 3,
                    'weight': 0.9
                },
                {
                    'purpose_code': 'EDUC',
                    'keywords': ['student', 'loan'],
                    'proximity': 3,
                    'weight': 0.8
                },
                {
                    'purpose_code': 'EDUC',
                    'keywords': ['course', 'registration'],
                    'proximity': 5,
                    'weight': 0.8
                }
            ]

            # Education-related terms for semantic similarity
            self.semantic_terms = [
                {'purpose_code': 'EDUC', 'term': 'education', 'threshold': 0.7, 'weight': 1.0},
                {'purpose_code': 'EDUC', 'term': 'tuition', 'threshold': 0.7, 'weight': 1.0},
                {'purpose_code': 'EDUC', 'term': 'school', 'threshold': 0.7, 'weight': 0.9},
                {'purpose_code': 'EDUC', 'term': 'college', 'threshold': 0.7, 'weight': 0.9},
                {'purpose_code': 'EDUC', 'term': 'university', 'threshold': 0.7, 'weight': 0.9},
                {'purpose_code': 'EDUC', 'term': 'student', 'threshold': 0.7, 'weight': 0.8},
                {'purpose_code': 'EDUC', 'term': 'academic', 'threshold': 0.7, 'weight': 0.8},
                {'purpose_code': 'EDUC', 'term': 'scholarship', 'threshold': 0.7, 'weight': 0.9},
                {'purpose_code': 'EDUC', 'term': 'course', 'threshold': 0.7, 'weight': 0.8}
            ]
    ```
  - [ ] Update `GoodsDomainEnhancer` to use semantic patterns
  - [ ] Update `InsuranceDomainEnhancer` to use semantic patterns
  - [ ] Update `ServicesDomainEnhancer` to use semantic patterns
  - [ ] Update `TechDomainEnhancer` to use semantic patterns
  - [ ] Update `TransportationDomainEnhancer` to use semantic patterns
  - [ ] Update `PropertyPurchaseEnhancer` to use semantic patterns
  - [ ] Update `CardPaymentEnhancer` to use semantic patterns
  - [ ] Update `CrossBorderEnhancer` to use semantic patterns
  - [ ] Update `CourtPaymentEnhancer` to use semantic patterns
  - [ ] Update `TargetedEnhancer` to use semantic patterns
  - [ ] Update `RareCodesEnhancer` to use semantic patterns
  - [ ] Update `PatternEnhancer` to use semantic patterns

- [ ] **5.3 Create Migration Script**
  - [ ] Implement script to convert existing enhancers to semantic enhancers
    ```python
    # scripts/migrate_enhancers_to_semantic.py

    import os
    import re
    import glob

    def migrate_enhancer(file_path):
        """Migrate an existing enhancer to use the semantic approach."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Update imports
        content = re.sub(
            r'from purpose_classifier\.domain_enhancers\.base_enhancer import BaseEnhancer',
            'from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer',
            content
        )

        # Update class definition
        content = re.sub(
            r'class (\w+)\(BaseEnhancer\):',
            r'class \1(SemanticEnhancer):',
            content
        )

        # Extract existing patterns and keywords
        patterns = extract_patterns(content)

        # Create _initialize_patterns method
        init_pattern = re.compile(r'def __init__\(self\):(.*?)def', re.DOTALL)
        if init_match := init_pattern.search(content):
            init_content = init_match.group(1)
            new_init = f"""def __init__(self):
        super().__init__()
        self._initialize_patterns()

    def _initialize_patterns(self):
        \"\"\"Initialize semantic patterns and contexts.\"\"\"
        # Direct keywords with purpose codes
        self.direct_keywords = {patterns['keywords']}

        # Semantic context patterns
        self.context_patterns = {patterns['context_patterns']}

        # Semantic terms for similarity matching
        self.semantic_terms = {patterns['semantic_terms']}

    def"""
            content = init_pattern.sub(new_init, content)

        # Save updated file
        with open(file_path, 'w') as f:
            f.write(content)

    def extract_patterns(content):
        """Extract patterns and keywords from existing enhancer."""
        # This is a simplified implementation
        # In practice, this would need to be more sophisticated
        patterns = {
            'keywords': '{}',
            'context_patterns': '[]',
            'semantic_terms': '[]'
        }

        # Extract keywords
        keyword_pattern = re.compile(r'self\.(\w+)_keywords\s*=\s*\[(.*?)\]', re.DOTALL)
        for match in keyword_pattern.finditer(content):
            keyword_type = match.group(1)
            keywords = match.group(2)
            # Process keywords and add to patterns

        # Extract patterns
        pattern_pattern = re.compile(r'self\.(\w+)_patterns\s*=\s*\[(.*?)\]', re.DOTALL)
        for match in pattern_pattern.finditer(content):
            pattern_type = match.group(1)
            patterns_text = match.group(2)
            # Process patterns and add to patterns

        return patterns

    def migrate_all_enhancers():
        """Migrate all existing enhancers to use the semantic approach."""
        enhancer_files = glob.glob('purpose_classifier/domain_enhancers/*_enhancer.py')
        for file_path in enhancer_files:
            if 'base_enhancer.py' not in file_path and 'semantic_enhancer.py' not in file_path:
                print(f"Migrating {file_path}...")
                migrate_enhancer(file_path)

    if __name__ == '__main__':
        migrate_all_enhancers()
    ```
  - [ ] Test migration script on sample enhancers
  - [ ] Document migration process

- [ ] **5.4 Test Revamped Enhancers**
  - [ ] Create comprehensive test suite for all revamped enhancers
  - [ ] Compare performance before and after migration
  - [ ] Identify and fix any regressions
  - [ ] Optimize enhancer chain for maximum accuracy

## Phase 6: Integration and Optimization

- [ ] **6.1 Enhancer Integration**
  - [ ] Update EnhancerManager to use new enhancers
  - [ ] Optimize enhancer chain for maximum accuracy
  - [ ] Implement enhancer collaboration mechanisms
  - [ ] Add conflict resolution for competing enhancers
  - [ ] Test with comprehensive test suite

- [ ] **6.2 Performance Optimization**
  - [ ] Profile enhancer performance
  - [ ] Optimize word embedding loading and usage
  - [ ] Implement caching for semantic similarity calculations
  - [ ] Reduce redundant pattern matching
  - [ ] Test performance with large datasets

- [ ] **6.3 Confidence Calibration**
  - [ ] Analyze confidence scores across enhancers
  - [ ] Calibrate confidence thresholds for optimal performance
  - [ ] Implement adaptive confidence scoring
  - [ ] Test with confidence-specific test cases

## Phase 7: Validation and Refinement

- [ ] **7.1 Comprehensive Testing**
  - [ ] Run full test suite with all enhancers
  - [ ] Measure overall accuracy, precision, recall, and F1-score
  - [ ] Identify remaining problematic cases
  - [ ] Create additional test cases for edge cases

- [ ] **7.2 Error Analysis**
  - [ ] Analyze misclassifications
  - [ ] Identify patterns in errors
  - [ ] Categorize error types
  - [ ] Prioritize error types for fixing

- [ ] **7.3 Iterative Refinement**
  - [ ] Refine semantic patterns based on error analysis
  - [ ] Adjust confidence thresholds and weights
  - [ ] Fine-tune enhancer priorities
  - [ ] Retest with full test suite

## Phase 8: Documentation and Deployment

- [ ] **8.1 Code Documentation**
  - [ ] Document all new classes and methods
  - [ ] Create usage examples
  - [ ] Document enhancer decision process
  - [ ] Create architecture diagrams

- [ ] **8.2 User Documentation**
  - [ ] Update README with new features
  - [ ] Create usage guidelines
  - [ ] Document configuration options
  - [ ] Add troubleshooting section

- [ ] **8.3 Deployment**
  - [ ] Create deployment package
  - [ ] Implement version control
  - [ ] Add migration guide for existing users
  - [ ] Create release notes

## Implementation Timeline

1. **Phase 1: Foundation** - 1 week
2. **Phase 2: Specialized Enhancers** - 2 weeks
3. **Phase 3: Message Type Context Awareness** - 1 week
4. **Phase 4: Category Purpose Code Mapping** - 1 week
5. **Phase 5: Revamping Existing Enhancers** - 2 weeks
6. **Phase 6: Integration and Optimization** - 1 week
7. **Phase 7: Validation and Refinement** - 1 week
8. **Phase 8: Documentation and Deployment** - 1 week

**Total Estimated Time: 10 weeks**

## Success Criteria

- Overall accuracy reaches 90% or higher
- Each purpose code achieves at least 80% accuracy
- Category purpose code accuracy reaches at least 75%
- OTHR usage remains at 0%
- Performance remains acceptable (classification time < 100ms per transaction)

## Monitoring and Maintenance

After deployment, continue to:
- Monitor accuracy in production
- Collect feedback from users
- Add new test cases for emerging patterns
- Refine enhancers based on real-world usage
- Update word embeddings periodically to capture new terminology

## Summary: Key Components of Semantic Pattern Matching Approach

The semantic pattern matching approach described in this implementation plan offers several advantages over traditional keyword-based pattern matching:

1. **Semantic Understanding**: By using word embeddings and semantic similarity, the system can understand the meaning behind transactions even when exact keywords are not present.

2. **Context Awareness**: The proximity-based pattern matching allows the system to understand the context of words, not just their presence.

3. **Confidence Calibration**: The weighted confidence scoring mechanism ensures that predictions are made with appropriate confidence levels.

4. **Specialized Enhancers**: Dedicated enhancers for problematic purpose codes (DIVD, LOAN/LOAR, TRAD) provide domain-specific semantic understanding.

5. **Prioritized Processing**: The enhanced priority system ensures that the most relevant enhancers are applied first, with appropriate confidence thresholds.

6. **Comprehensive Testing**: The improved testing framework with cross-validation and detailed metrics tracking ensures robust evaluation.

7. **Transparent Decision Process**: The enhanced logging system provides transparency into the decision-making process.

By implementing this plan, we expect to achieve the target of 90% overall accuracy, with significant improvements in problematic purpose codes like DIVD, LOAN/LOAR, and TRAD, while maintaining 0% OTHR usage.
