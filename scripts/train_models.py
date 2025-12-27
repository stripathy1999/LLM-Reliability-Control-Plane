"""
ML Model Training Script

Pre-trains all ML models with synthetic data to ensure they work correctly.
Run this script before demo to have trained models ready.

Usage:
    python scripts/train_models.py
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml_training import train_all_models, generate_synthetic_training_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Train all ML models with synthetic data."""
    logger.info("=" * 60)
    logger.info("ML Model Training Script")
    logger.info("=" * 60)
    
    # Generate synthetic training data
    logger.info("\n1. Generating synthetic training data...")
    logger.info("   Generating 30 days of hourly data points...")
    
    training_data = generate_synthetic_training_data(days=30)
    logger.info(f"   ✓ Generated {len(training_data)} data points")
    logger.info(f"   ✓ Time range: {training_data[0]['timestamp']} to {training_data[-1]['timestamp']}")
    
    # Show sample data
    logger.info("\n   Sample data point:")
    sample = training_data[0]
    logger.info(f"   - Hour: {sample['hour_of_day']}, Day: {sample['day_of_week']}")
    logger.info(f"   - Requests: {sample['request_count']}")
    logger.info(f"   - Input tokens: {sample['avg_input_tokens']}")
    logger.info(f"   - Output tokens: {sample['avg_output_tokens']}")
    logger.info(f"   - Cost: ${sample['cost_usd']:.6f}")
    
    # Train all models
    logger.info("\n2. Training ML models...")
    logger.info("   This may take a few minutes...")
    
    results = train_all_models(training_data)
    
    # Display results
    logger.info("\n3. Training Results:")
    logger.info("=" * 60)
    
    if 'error' in results:
        logger.error(f"   ✗ Training failed: {results['error']}")
        return 1
    
    logger.info(f"   ✓ Training samples: {results.get('training_samples', 0)}")
    logger.info(f"   ✓ Timestamp: {results.get('timestamp', 'unknown')}")
    
    # Cost predictor results
    cost_result = results.get('results', {}).get('cost_predictor', {})
    if 'error' in cost_result:
        logger.warning(f"   ⚠ Cost predictor: {cost_result['error']}")
    else:
        logger.info(f"   ✓ Cost predictor trained:")
        logger.info(f"     - Status: {cost_result.get('status', 'unknown')}")
        logger.info(f"     - MAE: {cost_result.get('mae', 0):.6f}")
        logger.info(f"     - R² Score: {cost_result.get('r2_score', 0):.4f}")
        logger.info(f"     - Training samples: {cost_result.get('training_samples', 0)}")
        logger.info(f"     - Test samples: {cost_result.get('test_samples', 0)}")
    
    # Quality predictor results
    quality_result = results.get('results', {}).get('quality_predictor', {})
    if 'error' in quality_result:
        logger.warning(f"   ⚠ Quality predictor: {quality_result['error']}")
    else:
        logger.info(f"   ✓ Quality baseline established:")
        logger.info(f"     - Status: {quality_result.get('status', 'unknown')}")
        logger.info(f"     - Baseline samples: {quality_result.get('baseline_samples', 0)}")
        logger.info(f"     - Mean similarity: {quality_result.get('baseline_mean_similarity', 0):.3f}")
        logger.info(f"     - Std deviation: {quality_result.get('baseline_std', 0):.3f}")
    
    # Check if models were saved
    logger.info("\n4. Model Files:")
    logger.info("=" * 60)
    
    models_dir = Path(__file__).parent.parent / "models"
    if models_dir.exists():
        model_files = list(models_dir.glob("*.pkl"))
        if model_files:
            logger.info(f"   ✓ Found {len(model_files)} model files:")
            for model_file in model_files:
                size_kb = model_file.stat().st_size / 1024
                logger.info(f"     - {model_file.name} ({size_kb:.1f} KB)")
        else:
            logger.warning("   ⚠ No model files found (models may not have been saved)")
    else:
        logger.warning(f"   ⚠ Models directory not found: {models_dir}")
        logger.info(f"   Creating models directory...")
        models_dir.mkdir(exist_ok=True)
        logger.info(f"   ✓ Created: {models_dir}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Training Complete! ✓")
    logger.info("=" * 60)
    logger.info("\nModels are now ready to use:")
    logger.info("  - Cost prediction: app.ml_cost_predictor.CostPredictor")
    logger.info("  - Quality prediction: app.ml_quality_predictor.QualityPredictor")
    logger.info("  - Model routing: app.model_router.ModelRouter")
    logger.info("\nYou can now run the application and use ML features!")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


