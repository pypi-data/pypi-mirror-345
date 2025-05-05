#!/usr/bin/env python
"""
Example script for migrating enhancers to use the semantic approach.

This script demonstrates how to use the migrate_enhancers_to_semantic.py script
to convert existing enhancers to use the semantic approach.
"""

import os
import sys
import logging
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.migrate_enhancers_to_semantic import migrate_enhancer, migrate_all_enhancers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Example script for migrating enhancers')
    parser.add_argument('--enhancer-dir', default='purpose_classifier/domain_enhancers',
                        help='Directory containing enhancer files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Do not actually modify files')
    parser.add_argument('--file', help='Migrate a specific file')
    
    args = parser.parse_args()
    
    print("Semantic Enhancer Migration Example")
    print("===================================")
    print("This script demonstrates how to use the migrate_enhancers_to_semantic.py script")
    print("to convert existing enhancers to use the semantic approach.")
    print()
    
    if args.file:
        print(f"Migrating a single file: {args.file}")
        if migrate_enhancer(args.file, args.dry_run):
            print(f"Successfully migrated {args.file}")
        else:
            print(f"Failed to migrate {args.file}")
    else:
        print(f"Migrating all enhancers in {args.enhancer_dir}")
        success_count, total_count = migrate_all_enhancers(args.enhancer_dir, args.dry_run)
        print(f"Successfully migrated {success_count} out of {total_count} enhancers")
    
    print()
    print("Migration complete!")
    print()
    print("Next steps:")
    print("1. Review the migrated enhancers to ensure they work as expected")
    print("2. Run tests to verify the migrated enhancers")
    print("3. Update the enhancer manager to use the new semantic enhancers")
    print("4. Update any code that uses the enhancers to use the new semantic enhancers")
    print()
    print("Example usage:")
    print("python -m scripts.migrate_enhancers_example --dry-run")
    print("python -m scripts.migrate_enhancers_example --file purpose_classifier/domain_enhancers/education_enhancer.py")
    print("python -m scripts.migrate_enhancers_example")

if __name__ == '__main__':
    main()
