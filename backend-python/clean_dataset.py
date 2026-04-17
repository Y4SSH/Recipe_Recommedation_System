#!/usr/bin/env python3
"""
Dataset cleaner and variant tagger.

Processes recipes_extended.csv to:
1. Detect duplicate recipes (same name, different content)
2. Extract and tag recipe variants (cooking method, protein type, etc.)
3. Normalize base recipe names
4. Calculate difficulty variance
5. Output cleaned CSV with new columns

New columns added:
  - base_recipe: normalized base recipe name
  - variant_type: specific variant (air_fryer, beef, slow_cooker, etc.)
  - cooking_method: cooking technique
  - protein_type: primary protein/ingredient type
  - difficulty_variance: similarity to base (0.0-1.0)
"""

import pandas as pd
import re
from collections import defaultdict
from difflib import SequenceMatcher
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VariantTagger:
    """Tags recipes with variant metadata based on name and attributes."""
    
    def __init__(self):
        # Cooking method patterns
        self.cooking_patterns = {
            'air_fryer': r'air\s?fryer|instant\s?pot|pressure\s?cooker',
            'slow_cooker': r'slow\s?cooker|crock\s?pot',
            'instant_pot': r'instant\s?pot|pressure\s?cooker',
            'baked': r'\bbaked?\b|\boven\b|\broasted?\b',
            'fried': r'\bfried?\b|\bfreeze\s?dried\b|\bcrispу?\b',
            'grilled': r'\bgrilled?\b|\bbbq\b|\bbarbecued?\b',
            'steamed': r'\bsteamed?\b',
            'boiled': r'\bboiled?\b|\bpoached?\b',
            'sauteed': r'\bsauteed?\b|\bstir\s?fry\b',
            'no_cook': r'\bno\s?cook\b|\bno\s?bake\b|\bcold\b|\braw\b',
        }
        
        # Protein patterns
        self.protein_patterns = {
            'chicken': r'\bchicken\b|\bpoultry\b',
            'beef': r'\bbeef\b|\bsteak\b|\bground\s?beef\b',
            'pork': r'\bpork\b|\bham\b|\bsausage\b|\bbacon\b',
            'fish': r'\bfish\b|\bsalmon\b|\btuna\b|\btrout\b|\bseafood\b',
            'shrimp': r'\bshrimp\b|\bprawn\b',
            'turkey': r'\bturkey\b',
            'lamb': r'\blamb\b',
            'vegetarian': r'\bvegetarian\b|\bveggies\b|\bveggie\b',
            'vegan': r'\bvegan\b',
            'sweet_potato': r'\bsweet\s?potato\b|\byam\b',
            'potato': r'\bpotato\b|\bfries\b',
            'tofu': r'\btofu\b',
            'cheese': r'\bcheese\b',
            'egg_dairy': r'\begg\b|\bdairy\b|\bcream\b|\bbutter\b',
        }
        
        # Difficulty modifiers
        self.difficulty_patterns = {
            'easy': r'\beasy\b|\bsimple\b|\bquick\b|\n15-minute\b|\b5-minute\b|\b10-minute\b',
            'complex': r'\badvanced\b|\bcomplex\b|\bchallenging\b|\btraditional\b|\nauthentic\b',
            'mini': r'\bmini\b|\bsmall\b|\nbites?\b',
            'fusion': r'\bfusion\b|\btacos\b|\bquesadilla\b|\bpizza\b',
        }
    
    def extract_cooking_method(self, title: str) -> str:
        """Extract cooking method from recipe title."""
        title_lower = title.lower()
        
        for method, pattern in self.cooking_patterns.items():
            if re.search(pattern, title_lower):
                return method
        
        return 'standard'
    
    def extract_protein_type(self, title: str, main_ingredient: str = None) -> str:
        """Extract primary protein type from recipe title or main ingredient."""
        title_lower = title.lower()
        ingredient_lower = main_ingredient.lower() if main_ingredient else ""
        
        combined = f"{title_lower} {ingredient_lower}"
        
        # Check in order of specificity
        for protein, pattern in self.protein_patterns.items():
            if re.search(pattern, combined):
                return protein
        
        return 'unknown'
    
    def extract_variant_type(self, title: str, cooking: str, protein: str) -> str:
        """Extract specific variant type for recipe."""
        title_lower = title.lower()
        
        # Check for specific variants based on title patterns
        variant_patterns = {
            'air_fryer': r'air\s?fryer',
            'slow_cooker': r'slow\s?cooker|crock\s?pot',
            'instant_pot': r'instant\s?pot',
            'sweet_potato': r'sweet\s?potato|\byam\b',
            'beef': r'\bbeef\b',
            'mini': r'\bmini\b|\bsmall\b',
            'traditional': r'\btraditional\b|\bclassic\b',
            'easy': r'\beasy\b|\bquick\b',
            'indian': r'\bindian\b|\bmakhani\b',
            'thai': r'\bthai\b',
            'mexican': r'\bmexican\b',
            'asian': r'\basian\b|\bchinese\b|\bkorean\b|\bjapanese\b',
        }
        
        for variant, pattern in variant_patterns.items():
            if re.search(pattern, title_lower):
                return variant
        
        # Fallback to cooking method if no other variant detected
        if cooking != 'standard':
            return cooking
        
        return 'standard'
    
    def normalize_base_recipe(self, title: str) -> str:
        """Normalize recipe title to extract base recipe name."""
        # Remove common modifiers
        modifiers = [
            r'\s*\(.*?\)',  # (parenthetical)
            r'\b(easy|quick|simple|amazing|best|perfect|authentic|traditional|chef\s?\w+\'s)\b',
            r'\b(air\s?fryer|slow\s?cooker|instant\s?pot|pressure\s?cooker)\b',
            r'\b(mini|small|homemade|fresh|baked|fried|grilled|steamed)\b',
            r'\b(slow|fast|no\s?cook|no\s?bake)\b',
            r'\d+[\s\-]?(ingredient|minute|hour|day)',
        ]
        
        normalized = title.strip()
        for modifier in modifiers:
            normalized = re.sub(modifier, '', normalized, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove common suffixes
        normalized = re.sub(r'\s*-\s*$', '', normalized)
        
        return normalized if normalized else title
    
    def calculate_difficulty_variance(self, row: pd.Series, base_row: pd.Series) -> float:
        """
        Calculate how different this recipe is from the base.
        0.0 = identical, 1.0 = completely different.
        """
        if base_row is None:
            return 0.5  # neutral if no base
        
        try:
            # Compare ingredient count
            ing_diff = abs(row.get('num_ingredients', 0) - base_row.get('num_ingredients', 0))
            ing_score = min(ing_diff / 20.0, 1.0)  # normalize
            
            # Compare step count
            steps_diff = abs(row.get('num_steps', 0) - base_row.get('num_steps', 0))
            steps_score = min(steps_diff / 15.0, 1.0)
            
            # Compare difficulty
            diff_same = row.get('difficulty') == base_row.get('difficulty')
            diff_score = 0.0 if diff_same else 0.3
            
            # Average
            variance = (ing_score + steps_score + diff_score) / 3.0
            return min(variance, 1.0)
        except:
            return 0.5


def clean_dataset(input_csv: str, output_csv: str, sample_size: int = None) -> dict:
    """
    Clean and tag dataset with variant metadata.
    
    Args:
        input_csv: Path to input CSV
        output_csv: Path to output CSV
        sample_size: Optional sample size for testing (None = full dataset)
    
    Returns:
        dict: Statistics about the cleaning process
    """
    logger.info(f"Loading dataset from {input_csv}")
    df = pd.read_csv(input_csv, low_memory=False)
    
    if sample_size:
        df = df.sample(n=min(sample_size, len(df)), random_state=42)
        logger.info(f"Using sample of {len(df)} recipes")
    
    logger.info(f"Loaded {len(df)} recipes with {len(df.columns)} columns")
    
    # Initialize tagger
    tagger = VariantTagger()
    
    # Initialize new columns
    df['base_recipe'] = ''
    df['variant_type'] = ''
    df['cooking_method'] = ''
    df['protein_type'] = ''
    df['difficulty_variance'] = 0.0
    
    # Group by normalized title to find variants
    logger.info("Detecting recipe groups and variants...")
    recipe_groups = defaultdict(list)
    
    for idx, row in df.iterrows():
        title = row['recipe_title']
        title_normalized = tagger.normalize_base_recipe(title)
        recipe_groups[title_normalized].append(idx)
    
    logger.info(f"Found {len(recipe_groups)} recipe groups")
    
    # Process each recipe
    logger.info("Tagging recipes...")
    stats = {
        'total': len(df),
        'duplicates': 0,
        'variants': 0,
        'standalone': 0,
    }
    
    for base_name, indices in recipe_groups.items():
        if len(indices) > 1:
            stats['duplicates'] += len(indices)
            
            # Find best representative (most ingredients)
            best_idx = max(indices, key=lambda i: df.loc[i, 'num_ingredients'] or 0)
            base_row = df.loc[best_idx]
        else:
            best_idx = indices[0]
            base_row = df.loc[best_idx]
            stats['standalone'] += 1
        
        # Tag all recipes in group
        for idx in indices:
            row = df.loc[idx]
            
            # Extract metadata
            cooking = tagger.extract_cooking_method(row['recipe_title'])
            protein = tagger.extract_protein_type(row['recipe_title'], row.get('main_ingredient'))
            variant = tagger.extract_variant_type(row['recipe_title'], cooking, protein)
            variance = tagger.calculate_difficulty_variance(row, base_row)
            
            # Assign values
            df.at[idx, 'base_recipe'] = base_name
            df.at[idx, 'cooking_method'] = cooking
            df.at[idx, 'protein_type'] = protein
            df.at[idx, 'variant_type'] = variant
            df.at[idx, 'difficulty_variance'] = variance
            
            if idx != best_idx:
                stats['variants'] += 1
    
    # Save cleaned dataset
    logger.info(f"Saving cleaned dataset to {output_csv}")
    
    # Reorder columns: new ones at end
    col_order = [col for col in df.columns if col not in [
        'base_recipe', 'variant_type', 'cooking_method', 'protein_type', 'difficulty_variance'
    ]] + ['base_recipe', 'variant_type', 'cooking_method', 'protein_type', 'difficulty_variance']
    
    df = df[col_order]
    df.to_csv(output_csv, index=False)
    
    logger.info(f"Cleaned dataset saved: {output_csv}")
    logger.info(f"\nStatistics:")
    logger.info(f"  Total recipes: {stats['total']}")
    logger.info(f"  Duplicate/variant entries: {stats['duplicates']}")
    logger.info(f"  Variant recipes tagged: {stats['variants']}")
    logger.info(f"  Standalone recipes: {stats['standalone']}")
    
    # Sample output
    logger.info(f"\nSample tagged recipes:")
    sample_cols = ['recipe_title', 'base_recipe', 'variant_type', 'cooking_method', 'protein_type', 'difficulty_variance']
    for idx in df.sample(min(5, len(df))).index:
        logger.info(f"\n  Title: {df.loc[idx, 'recipe_title']}")
        logger.info(f"    Base: {df.loc[idx, 'base_recipe']}")
        logger.info(f"    Variant: {df.loc[idx, 'variant_type']}")
        logger.info(f"    Cooking: {df.loc[idx, 'cooking_method']}")
        logger.info(f"    Protein: {df.loc[idx, 'protein_type']}")
        logger.info(f"    Variance: {df.loc[idx, 'difficulty_variance']:.2f}")
    
    return stats


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean and tag recipe dataset')
    parser.add_argument('--input', '-i', default='../recipes_extended.csv', 
                       help='Input CSV path (default: ../recipes_extended.csv)')
    parser.add_argument('--output', '-o', default='../recipes_cleaned.csv',
                       help='Output CSV path (default: ../recipes_cleaned.csv)')
    parser.add_argument('--sample', '-s', type=int, default=None,
                       help='Sample size for testing (default: None = full dataset)')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='Run validation on sample before full run')
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("RECIPE DATASET CLEANER & VARIANT TAGGER")
    logger.info("=" * 80)
    
    if args.validate:
        logger.info("\nRUNNING VALIDATION (sample=5000)...")
        stats = clean_dataset(args.input, args.output.replace('.csv', '_sample.csv'), sample_size=5000)
        logger.info("\nValidation complete. Run without --validate for full dataset.")
    else:
        stats = clean_dataset(args.input, args.output, sample_size=args.sample)
        logger.info("\nCleaning complete!")
