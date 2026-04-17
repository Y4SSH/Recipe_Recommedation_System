#!/usr/bin/env python3
"""
Database migration script to add variant tagging columns.

Adds the following columns to recipes table:
  - base_recipe (VARCHAR): Normalized base recipe name
  - variant_type (VARCHAR): Specific variant (air_fryer, beef, slow_cooker, etc.)
  - cooking_method (VARCHAR): Cooking technique
  - protein_type (VARCHAR): Primary protein/ingredient type
  - difficulty_variance (REAL): Similarity to base (0.0-1.0)

Usage:
  python migrate_add_variant_columns.py
  python migrate_add_variant_columns.py --rollback
  python migrate_add_variant_columns.py --database recipes.db
"""

import sqlite3
import logging
import argparse
from pathlib import Path
from datetime import datetime
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_recipe_table_name(conn: sqlite3.Connection) -> str:
    """Resolve the recipe table name for this database."""
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    if 'recipes' in tables:
        return 'recipes'
    if 'Recipe' in tables:
        return 'Recipe'

    raise RuntimeError(f"Could not find recipe table. Available tables: {sorted(tables)}")


def backup_database(db_path: str) -> str:
    """Create backup of database before migration."""
    db_path = Path(db_path)
    backup_dir = db_path.parent / 'db_backups'
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'recipes_backup_{timestamp}_before_variant_migration.db'
    
    logger.info(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    logger.info(f"Backup created successfully")
    
    return str(backup_path)


def check_columns_exist(conn: sqlite3.Connection) -> dict:
    """Check which columns already exist."""
    table_name = get_recipe_table_name(conn)
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    existing_cols = {row[1] for row in cursor.fetchall()}
    
    new_cols = {
        'base_recipe': 'base_recipe' in existing_cols,
        'variant_type': 'variant_type' in existing_cols,
        'cooking_method': 'cooking_method' in existing_cols,
        'protein_type': 'protein_type' in existing_cols,
        'difficulty_variance': 'difficulty_variance' in existing_cols,
    }
    
    return new_cols


def migrate_up(db_path: str) -> bool:
    """Add variant tagging columns to database."""
    logger.info("=" * 80)
    logger.info("DATABASE MIGRATION: ADD VARIANT TAGGING COLUMNS")
    logger.info("=" * 80)
    
    db_path = Path(db_path)
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        table_name = get_recipe_table_name(conn)
        
        # Check current state
        existing = check_columns_exist(conn)
        already_exist = [col for col, exists in existing.items() if exists]
        pending_cols = [col for col, exists in existing.items() if not exists]
        
        if not pending_cols:
            logger.warning(f"Columns already exist: {already_exist}")
            logger.info("Migration already applied. Skipping.")
            conn.close()
            return True
        
        # Backup before migration
        backup_file = backup_database(str(db_path))
        
        # Add new columns
        logger.info(f"\nAdding columns to {table_name} table...")
        
        columns_to_add = [
            ('base_recipe', 'VARCHAR(255)', 'Normalized base recipe name'),
            ('variant_type', 'VARCHAR(100)', 'Specific variant (air_fryer, beef, slow_cooker, etc.)'),
            ('cooking_method', 'VARCHAR(100)', 'Cooking technique (baked, fried, slow_cooker, etc.)'),
            ('protein_type', 'VARCHAR(100)', 'Primary protein type (chicken, beef, vegetarian, etc.)'),
            ('difficulty_variance', 'REAL', 'Similarity to base recipe (0.0-1.0)'),
        ]
        
        for col_name, col_type, description in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} DEFAULT NULL")
                logger.info(f"  + Added {col_name} ({col_type})")
            except sqlite3.OperationalError as e:
                if 'already exists' in str(e):
                    logger.info(f"  ~ {col_name} already exists, skipping")
                else:
                    raise
        
        # Create index on base_recipe for faster filtering
        logger.info("\nCreating index on base_recipe...")
        try:
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS idx_recipe_base_recipe "
                f"ON {table_name}(base_recipe)"
            )
            logger.info("  + Index created on base_recipe")
        except sqlite3.OperationalError as e:
            logger.warning(f"  ! Could not create index: {e}")
        
        # Commit changes
        conn.commit()
        logger.info("\nMigration completed successfully!")
        logger.info(f"Backup saved: {backup_file}")
        logger.info("New columns are ready for population via import_data.py")
        
        # Summary
        logger.info("\nMigration Summary:")
        logger.info(f"  - Added 5 new columns to {table_name} table")
        logger.info(f"  - All columns are nullable (can be populated on import)")
        logger.info(f"  - Index created for efficient variant queries")
        logger.info(f"  - Database backup: {backup_file}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def migrate_down(db_path: str) -> bool:
    """Remove variant tagging columns from database (rollback)."""
    logger.info("=" * 80)
    logger.info("DATABASE ROLLBACK: REMOVE VARIANT TAGGING COLUMNS")
    logger.info("=" * 80)
    
    db_path = Path(db_path)
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return False
    
    logger.warning("WARNING: This will drop the variant tagging columns!")
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        logger.info("Rollback cancelled")
        return False
    
    try:
        # Backup before rollback
        backup_file = backup_database(str(db_path))
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        table_name = get_recipe_table_name(conn)
        
        # Check if columns exist
        existing = check_columns_exist(conn)
        cols_to_drop = [col for col, exists in existing.items() if exists]
        
        if not cols_to_drop:
            logger.info("No variant columns found. Nothing to rollback.")
            conn.close()
            return True
        
        logger.info(f"\nRemoving columns: {cols_to_drop}")
        
        # SQLite doesn't support ALTER TABLE DROP COLUMN directly in older versions
        # We need to recreate the table without those columns
        logger.info(f"Recreating {table_name} table without variant columns...")
        
        # Get current table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        all_cols = [(row[1], row[2]) for row in cursor.fetchall()]
        keep_cols = [(col, type_) for col, type_ in all_cols 
                     if col not in cols_to_drop]
        
        # Create temporary table with kept columns
        col_defs = ', '.join([f"{col} {type_}" for col, type_ in keep_cols])
        cursor.execute(f"ALTER TABLE {table_name} RENAME TO {table_name}_old")
        cursor.execute(f"CREATE TABLE {table_name} ({col_defs})")
        
        # Copy data
        keep_col_names = ', '.join([col for col, _ in keep_cols])
        cursor.execute(
            f"INSERT INTO {table_name} ({keep_col_names}) "
            f"SELECT {keep_col_names} FROM {table_name}_old"
        )
        
        # Drop old table
        cursor.execute(f"DROP TABLE {table_name}_old")
        
        conn.commit()
        logger.info("Rollback completed successfully!")
        logger.info(f"Backup saved: {backup_file}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        logger.error("You can restore from backup manually if needed")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database migration for variant tagging columns')
    parser.add_argument('--database', '-d', default='recipes.db',
                       help='Database path (default: recipes.db)')
    parser.add_argument('--rollback', '-r', action='store_true',
                       help='Rollback migration (remove variant columns)')
    parser.add_argument('--check', '-c', action='store_true',
                       help='Check if migration has been applied')
    
    args = parser.parse_args()
    
    if args.check:
        try:
            conn = sqlite3.connect(args.database)
            existing = check_columns_exist(conn)
            applied = [col for col, exists in existing.items() if exists]
            pending = [col for col, exists in existing.items() if not exists]
            
            logger.info("Migration Status:")
            if applied:
                logger.info(f"  Applied: {applied}")
            if pending:
                logger.info(f"  Pending: {pending}")
            if not applied and not pending:
                logger.info("  Migration not yet applied")
            
            conn.close()
        except Exception as e:
            logger.error(f"Could not check status: {e}")
    elif args.rollback:
        success = migrate_down(args.database)
        exit(0 if success else 1)
    else:
        success = migrate_up(args.database)
        exit(0 if success else 1)
