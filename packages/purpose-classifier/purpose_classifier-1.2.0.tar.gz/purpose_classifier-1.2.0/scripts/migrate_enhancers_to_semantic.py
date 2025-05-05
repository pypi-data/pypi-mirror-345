#!/usr/bin/env python
"""
Migration script to convert existing enhancers to use the semantic approach.

This script:
1. Identifies existing enhancers that need to be migrated
2. Updates their imports to use SemanticEnhancer
3. Updates their class definitions to inherit from SemanticEnhancer
4. Extracts existing patterns and keywords
5. Creates _initialize_patterns method
6. Updates enhance_classification method if needed
"""

import os
import re
import glob
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_keywords(content):
    """
    Extract keywords from existing enhancer.

    Args:
        content: File content as string

    Returns:
        dict: Dictionary of purpose code to keywords
    """
    keywords = {}

    # Look for keyword dictionaries
    keyword_pattern = re.compile(r'self\.(\w+)_keywords\s*=\s*{(.*?)}', re.DOTALL)
    for match in keyword_pattern.finditer(content):
        keyword_type = match.group(1)
        keywords_text = match.group(2)

        # Try to extract purpose code from keyword type
        purpose_code = keyword_type.upper()
        if purpose_code == "EDUCATION":
            purpose_code = "EDUC"
        elif purpose_code == "GOODS":
            purpose_code = "GDDS"
        elif purpose_code == "SERVICES":
            purpose_code = "SCVE"
        elif purpose_code == "INSURANCE":
            purpose_code = "INSU"

        # Extract keywords
        keyword_items = []
        for line in keywords_text.split('\n'):
            if ':' in line:
                key_match = re.search(r'"([^"]+)"', line)
                if key_match:
                    keyword = key_match.group(1)
                    keyword_items.append(f'"{keyword}"')

        if keyword_items:
            keywords[purpose_code] = f"[{', '.join(keyword_items)}]"

    # Look for keyword lists
    list_pattern = re.compile(r'self\.(\w+)_keywords\s*=\s*\[(.*?)\]', re.DOTALL)
    for match in list_pattern.finditer(content):
        keyword_type = match.group(1)
        keywords_text = match.group(2)

        # Try to extract purpose code from keyword type
        purpose_code = keyword_type.upper()
        if purpose_code == "EDUCATION":
            purpose_code = "EDUC"
        elif purpose_code == "GOODS":
            purpose_code = "GDDS"
        elif purpose_code == "SERVICES":
            purpose_code = "SCVE"
        elif purpose_code == "INSURANCE":
            purpose_code = "INSU"

        # Extract keywords
        keyword_items = []
        for line in keywords_text.split('\n'):
            if '"' in line or "'" in line:
                key_match = re.search(r'["\'](.*?)["\']', line)
                if key_match:
                    keyword = key_match.group(1)
                    keyword_items.append(f'"{keyword}"')

        if keyword_items:
            keywords[purpose_code] = f"[{', '.join(keyword_items)}]"

    # Format as dictionary
    if keywords:
        keywords_str = "{\n"
        for purpose_code, keyword_list in keywords.items():
            keywords_str += f"            '{purpose_code}': {keyword_list},\n"
        keywords_str += "        }"
        return keywords_str

    return "{}"

def extract_patterns(content):
    """
    Extract patterns from existing enhancer.

    Args:
        content: File content as string

    Returns:
        str: String representation of context patterns list
    """
    patterns = []

    # Look for pattern lists
    pattern_pattern = re.compile(r'self\.(\w+)_patterns\s*=\s*\[(.*?)\]', re.DOTALL)
    for match in pattern_pattern.finditer(content):
        pattern_type = match.group(1)
        patterns_text = match.group(2)

        # Try to extract purpose code from pattern type
        purpose_code = pattern_type.upper()
        if purpose_code == "EDUCATION":
            purpose_code = "EDUC"
        elif purpose_code == "GOODS":
            purpose_code = "GDDS"
        elif purpose_code == "SERVICES":
            purpose_code = "SCVE"
        elif purpose_code == "INSURANCE":
            purpose_code = "INSU"

        # Extract patterns
        for line in patterns_text.split('\n'):
            if 'r"' in line or "r'" in line:
                try:
                    # Use a safer approach to extract the pattern
                    if 'r"' in line:
                        parts = line.split('r"')
                        if len(parts) > 1:
                            pattern_part = parts[1].split('"')[0]
                            patterns.append({
                                'purpose_code': purpose_code,
                                'pattern': pattern_part,
                                'proximity': 5,  # Default proximity
                                'weight': 0.9    # Default weight
                            })
                    elif "r'" in line:
                        parts = line.split("r'")
                        if len(parts) > 1:
                            pattern_part = parts[1].split("'")[0]
                            patterns.append({
                                'purpose_code': purpose_code,
                                'pattern': pattern_part,
                                'proximity': 5,  # Default proximity
                                'weight': 0.9    # Default weight
                            })
                except Exception as e:
                    logger.warning(f"Error extracting pattern from line: {line}. Error: {str(e)}")

    # Look for regex patterns in the content
    try:
        # Use a safer approach to extract regex patterns
        lines = content.split('\n')
        for line in lines:
            if 're.compile' in line or 'r"' in line or "r'" in line:
                try:
                    # Try to determine purpose code from surrounding context
                    purpose_code = "OTHR"  # Default
                    if "education" in line.lower():
                        purpose_code = "EDUC"
                    elif "goods" in line.lower():
                        purpose_code = "GDDS"
                    elif "service" in line.lower():
                        purpose_code = "SCVE"
                    elif "insurance" in line.lower():
                        purpose_code = "INSU"

                    # Extract the pattern
                    if 'r"' in line:
                        parts = line.split('r"')
                        if len(parts) > 1:
                            pattern_part = parts[1].split('"')[0]
                            patterns.append({
                                'purpose_code': purpose_code,
                                'pattern': pattern_part,
                                'proximity': 5,  # Default proximity
                                'weight': 0.8    # Default weight
                            })
                    elif "r'" in line:
                        parts = line.split("r'")
                        if len(parts) > 1:
                            pattern_part = parts[1].split("'")[0]
                            patterns.append({
                                'purpose_code': purpose_code,
                                'pattern': pattern_part,
                                'proximity': 5,  # Default proximity
                                'weight': 0.8    # Default weight
                            })
                except Exception as e:
                    logger.warning(f"Error extracting regex pattern from line: {line}. Error: {str(e)}")
    except Exception as e:
        logger.warning(f"Error processing regex patterns: {str(e)}")

    # Format as list
    if patterns:
        patterns_str = "[\n"
        for pattern in patterns:
            patterns_str += f"            {{\n"
            patterns_str += f"                'purpose_code': '{pattern['purpose_code']}',\n"
            # Use a list of keywords instead of a regex pattern
            keywords = []
            if 'pattern' in pattern:
                # Convert regex pattern to keywords
                # Remove regex special characters and split by non-word chars
                try:
                    # Replace common regex patterns with spaces
                    simplified = pattern['pattern']
                    simplified = simplified.replace('\\b', ' ')
                    simplified = simplified.replace('\\s+', ' ')
                    simplified = simplified.replace('\\s', ' ')
                    simplified = simplified.replace('\\d+', ' ')
                    simplified = simplified.replace('\\w+', ' ')
                    simplified = re.sub(r'[\(\)\[\]\{\}\.\+\*\?\|\\\^\$]', ' ', simplified)

                    # Split by spaces and filter out empty strings
                    words = [w.strip() for w in simplified.split() if w.strip()]

                    # Add each word as a keyword
                    for word in words:
                        if len(word) > 2:  # Only add words with at least 3 characters
                            keywords.append(word)
                except Exception as e:
                    logger.warning(f"Error converting pattern to keywords: {str(e)}")

            if not keywords:
                # Fallback to using the purpose code as a keyword
                keywords = [pattern['purpose_code'].lower()]

            # Format keywords as a list
            keywords_str = ", ".join([f"'{k}'" for k in keywords])
            patterns_str += f"                'keywords': [{keywords_str}],\n"
            patterns_str += f"                'proximity': {pattern['proximity']},\n"
            patterns_str += f"                'weight': {pattern['weight']}\n"
            patterns_str += f"            }},\n"
        patterns_str += "        ]"
        return patterns_str

    return "[]"

def extract_semantic_terms(content, class_name):
    """
    Create semantic terms based on keywords and domain.

    Args:
        content: File content as string
        class_name: Name of the enhancer class

    Returns:
        str: String representation of semantic terms list
    """
    terms = []

    # Determine domain from class name
    domain = None
    if "Education" in class_name:
        domain = "EDUC"
        terms = [
            {'term': 'education', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'tuition', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'school', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'college', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'university', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'student', 'threshold': 0.7, 'weight': 0.8},
            {'term': 'academic', 'threshold': 0.7, 'weight': 0.8}
        ]
    elif "Goods" in class_name:
        domain = "GDDS"
        terms = [
            {'term': 'goods', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'merchandise', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'product', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'purchase', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'equipment', 'threshold': 0.7, 'weight': 0.8},
            {'term': 'hardware', 'threshold': 0.7, 'weight': 0.8},
            {'term': 'supplies', 'threshold': 0.7, 'weight': 0.8}
        ]
    elif "Service" in class_name:
        domain = "SCVE"
        terms = [
            {'term': 'service', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'consulting', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'professional', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'maintenance', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'repair', 'threshold': 0.7, 'weight': 0.8},
            {'term': 'installation', 'threshold': 0.7, 'weight': 0.8},
            {'term': 'support', 'threshold': 0.7, 'weight': 0.8}
        ]
    elif "Insurance" in class_name:
        domain = "INSU"
        terms = [
            {'term': 'insurance', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'policy', 'threshold': 0.7, 'weight': 1.0},
            {'term': 'premium', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'coverage', 'threshold': 0.7, 'weight': 0.9},
            {'term': 'claim', 'threshold': 0.7, 'weight': 0.8},
            {'term': 'insurer', 'threshold': 0.7, 'weight': 0.8},
            {'term': 'insured', 'threshold': 0.7, 'weight': 0.8}
        ]

    # Format as list
    if terms and domain:
        terms_str = "[\n"
        for term in terms:
            terms_str += f"            {{\n"
            terms_str += f"                'purpose_code': '{domain}',\n"
            terms_str += f"                'term': '{term['term']}',\n"
            terms_str += f"                'threshold': {term['threshold']},\n"
            terms_str += f"                'weight': {term['weight']}\n"
            terms_str += f"            }},\n"
        terms_str += "        ]"
        return terms_str

    return "[]"

def migrate_enhancer(file_path, dry_run=False):
    """
    Migrate an existing enhancer to use the semantic approach.

    Args:
        file_path: Path to the enhancer file
        dry_run: If True, don't actually modify the file

    Returns:
        bool: True if migration was successful
    """
    logger.info(f"Migrating {file_path}...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract class name
        class_match = re.search(r'class\s+(\w+)', content)
        if not class_match:
            logger.error(f"Could not find class definition in {file_path}")
            return False

        class_name = class_match.group(1)
        logger.info(f"Found class: {class_name}")

        # Update imports
        content = re.sub(
            r'import\s+re\s*\n',
            'import re\nfrom purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer\n',
            content
        )

        # Check if import already exists
        if 'from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer' not in content:
            # Add import after other imports
            import_match = re.search(r'(import.*\n+)', content)
            if import_match:
                import_end = import_match.end()
                content = (content[:import_end] +
                          'from purpose_classifier.domain_enhancers.semantic_enhancer import SemanticEnhancer\n' +
                          content[import_end:])

        # Update class definition
        content = re.sub(
            r'class\s+(\w+)(?:\(\w+\))?:',
            r'class \1(SemanticEnhancer):',
            content
        )

        # Extract patterns and keywords
        keywords = extract_keywords(content)
        patterns = extract_patterns(content)
        semantic_terms = extract_semantic_terms(content, class_name)

        # Create _initialize_patterns method
        init_pattern = re.compile(r'def\s+__init__\s*\(\s*self\s*\)\s*:(.*?)(?=\n\s*def|\Z)', re.DOTALL)
        if init_match := init_pattern.search(content):
            init_content = init_match.group(1)
            new_init = f"""def __init__(self):
        super().__init__()
        self._initialize_patterns()

    def _initialize_patterns(self):
        \"\"\"Initialize semantic patterns and contexts.\"\"\"
        # Direct keywords with purpose codes
        self.direct_keywords = {keywords}

        # Semantic context patterns
        self.context_patterns = {patterns}

        # Semantic terms for similarity matching
        self.semantic_terms = {semantic_terms}

    def"""
            content = init_pattern.sub(new_init, content)
        else:
            logger.warning(f"Could not find __init__ method in {file_path}")
            # Add __init__ method
            class_pattern = re.compile(r'class\s+(\w+)(?:\(\w+\))?:(.*?)(?=\n\s*def|\Z)', re.DOTALL)
            if class_match := class_pattern.search(content):
                class_content = class_match.group(2)
                new_class_content = f"""{class_content}
    def __init__(self):
        super().__init__()
        self._initialize_patterns()

    def _initialize_patterns(self):
        \"\"\"Initialize semantic patterns and contexts.\"\"\"
        # Direct keywords with purpose codes
        self.direct_keywords = {keywords}

        # Semantic context patterns
        self.context_patterns = {patterns}

        # Semantic terms for similarity matching
        self.semantic_terms = {semantic_terms}
"""
                content = class_pattern.sub(f'class {class_name}(SemanticEnhancer):{new_class_content}', content)

        # Check if enhance_classification method exists
        if 'def enhance_classification' not in content:
            # Add enhance_classification method
            content += f"""
    def enhance_classification(self, result, narration, message_type=None):
        \"\"\"
        Enhance classification for {class_name.lower().replace('enhancer', '').replace('domain', '')}-related transactions.

        Args:
            result: Initial classification result
            narration: Transaction narration
            message_type: Optional message type

        Returns:
            dict: Enhanced classification result
        \"\"\"
        # Call the base implementation first
        enhanced_result = super().enhance_classification(result, narration, message_type)

        # If the base implementation didn't change anything, apply domain-specific logic
        if enhanced_result == result:
            # Get current purpose code and confidence
            purpose_code = result.get('purpose_code', 'OTHR')
            confidence = result.get('confidence', 0.0)

            # Add your domain-specific logic here

        return enhanced_result
"""

        # Save updated file
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Successfully migrated {file_path}")
        else:
            logger.info(f"Dry run: would have updated {file_path}")

        return True

    except Exception as e:
        logger.error(f"Error migrating {file_path}: {str(e)}")
        return False

def migrate_all_enhancers(enhancer_dir, dry_run=False):
    """
    Migrate all existing enhancers to use the semantic approach.

    Args:
        enhancer_dir: Directory containing enhancer files
        dry_run: If True, don't actually modify the files

    Returns:
        tuple: (success_count, total_count)
    """
    enhancer_files = glob.glob(os.path.join(enhancer_dir, '*_enhancer.py'))
    success_count = 0
    total_count = 0

    for file_path in enhancer_files:
        # Skip files that are already semantic enhancers
        if 'semantic_enhancer.py' in file_path:
            continue

        # Skip files that already have semantic in the name
        if '_semantic.py' in file_path:
            continue

        total_count += 1
        if migrate_enhancer(file_path, dry_run):
            success_count += 1

    return success_count, total_count

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Migrate enhancers to semantic approach')
    parser.add_argument('--enhancer-dir', default='purpose_classifier/domain_enhancers',
                        help='Directory containing enhancer files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Do not actually modify files')
    parser.add_argument('--file', help='Migrate a specific file')

    args = parser.parse_args()

    if args.file:
        if migrate_enhancer(args.file, args.dry_run):
            logger.info(f"Successfully migrated {args.file}")
        else:
            logger.error(f"Failed to migrate {args.file}")
    else:
        success_count, total_count = migrate_all_enhancers(args.enhancer_dir, args.dry_run)
        logger.info(f"Successfully migrated {success_count} out of {total_count} enhancers")

if __name__ == '__main__':
    main()
