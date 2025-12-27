"""
Start Background Services for Confluent Integration

This script starts all background services needed for:
- ML Pipeline processing
- Datadog Bridge
- Confluent Intelligence monitoring
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def start_ml_pipeline():
    """Start the ML pipeline for processing Kafka streams."""
    try:
        from app.stream_processors.ml_pipeline import get_ml_pipeline
        
        logger.info("Starting ML Pipeline...")
        pipeline = get_ml_pipeline()
        
        if not pipeline.enabled:
            logger.warning("ML Pipeline not enabled. Check Confluent configuration.")
            return
        
        logger.info("ML Pipeline started. Processing streams...")
        await pipeline.process_stream()
    except Exception as e:
        logger.error(f"Error starting ML Pipeline: {e}", exc_info=True)


async def start_datadog_bridge():
    """Start the Datadog bridge for ML insights."""
    try:
        from app.stream_processors.datadog_bridge import get_datadog_bridge
        
        logger.info("Starting Datadog Bridge...")
        bridge = get_datadog_bridge()
        
        if not bridge.enabled:
            logger.warning("Datadog Bridge not enabled. Check Confluent configuration.")
            return
        
        logger.info("Datadog Bridge started. Bridging ML insights...")
        bridge.bridge_ml_insights_to_datadog()
    except Exception as e:
        logger.error(f"Error starting Datadog Bridge: {e}", exc_info=True)


async def start_confluent_intelligence():
    """Start Confluent Intelligence monitoring."""
    try:
        from app.confluent_intelligence import get_confluent_intelligence
        
        logger.info("Starting Confluent Intelligence monitoring...")
        intelligence = get_confluent_intelligence()
        
        if not intelligence.enabled:
            logger.warning("Confluent Intelligence not enabled.")
            return
        
        logger.info("Confluent Intelligence monitoring started.")
        
        # Periodically get insights
        while True:
            try:
                health = intelligence.get_stream_health()
                logger.info(f"Stream Health: {health.get('health_score', 'N/A')}")
                
                cost = intelligence.get_cost_optimization()
                logger.info(f"Estimated Monthly Savings: ${cost.get('estimated_monthly_savings', 0)}")
                
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                logger.error(f"Error getting Confluent Intelligence insights: {e}")
                await asyncio.sleep(60)
    except Exception as e:
        logger.error(f"Error starting Confluent Intelligence: {e}", exc_info=True)


async def main():
    """Start all background services."""
    logger.info("=" * 60)
    logger.info("Starting Background Services for Confluent Integration")
    logger.info("=" * 60)
    
    # Start services concurrently
    tasks = []
    
    # Start ML Pipeline
    tasks.append(asyncio.create_task(start_ml_pipeline()))
    
    # Start Datadog Bridge (runs in separate thread)
    import threading
    bridge_thread = threading.Thread(
        target=lambda: asyncio.run(start_datadog_bridge()),
        daemon=True
    )
    bridge_thread.start()
    
    # Start Confluent Intelligence
    tasks.append(asyncio.create_task(start_confluent_intelligence()))
    
    # Wait for all tasks
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down background services...")
        for task in tasks:
            task.cancel()
        logger.info("Background services stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


