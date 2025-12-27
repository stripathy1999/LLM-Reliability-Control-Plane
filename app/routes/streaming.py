"""
Streaming Routes for Real-Time Dashboard

This module provides WebSocket endpoints for real-time streaming.
Note: Streaming endpoints are currently disabled as Confluent integration has been removed for Datadog-only submission.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/streaming", tags=["streaming"])

try:
    from confluent_kafka import Consumer
    CONFLUENT_AVAILABLE = True
except ImportError:
    CONFLUENT_AVAILABLE = False
    Consumer = None  # type: ignore[assignment, misc]


@router.websocket("/ws/health-score")
async def websocket_health_score(websocket: WebSocket):
    """
    Stream health scores in real-time from Kafka.
    
    This endpoint streams health score updates from the llm-health-scores
    Kafka topic to the frontend dashboard.
    """
    await websocket.accept()
    logger.info("WebSocket connection established for health scores")

    if not CONFLUENT_AVAILABLE:
        await websocket.send_json({
            "error": "Confluent not available",
            "message": "Health score streaming requires Confluent Kafka (removed for Datadog-only submission)"
        })
        await websocket.close()
        return
    
    # Confluent removed - endpoint disabled
    await websocket.send_json({
        "error": "Feature disabled",
        "message": "This endpoint requires Confluent Kafka which has been removed for Datadog-only submission"
    })
    await websocket.close()


@router.websocket("/ws/ml-insights")
async def websocket_ml_insights(websocket: WebSocket):
    """
    Stream ML insights in real-time from Confluent Kafka.
    
    This endpoint streams ML predictions and insights from the llm-ml-insights
    Kafka topic to the frontend dashboard.
    """
    await websocket.accept()
    logger.info("WebSocket connection established for ML insights")

    if not CONFLUENT_AVAILABLE:
        await websocket.send_json({
            "error": "Confluent not available",
            "message": "ML insights streaming requires Confluent Kafka (removed for Datadog-only submission)"
        })
        await websocket.close()
        return
    
    # Confluent removed - endpoint disabled
    await websocket.send_json({
        "error": "Feature disabled",
        "message": "This endpoint requires Confluent Kafka which has been removed for Datadog-only submission"
    })
    await websocket.close()


@router.websocket("/ws/streaming-dashboard")
async def streaming_dashboard(websocket: WebSocket):
    """
    Unified streaming dashboard endpoint.
    
    Streams multiple Kafka topics:
    - llm-metrics: Real-time metrics
    - llm-ml-insights: ML predictions
    - anomalies_stream: Anomaly detections
    """
    await websocket.accept()
    logger.info("WebSocket connection established for streaming dashboard")

    if not CONFLUENT_AVAILABLE:
        await websocket.send_json({
            "error": "Confluent not available",
            "message": "Streaming dashboard requires Confluent Kafka (removed for Datadog-only submission)"
        })
        await websocket.close()
        return
    
    # Confluent removed - endpoint disabled
    await websocket.send_json({
        "error": "Feature disabled",
        "message": "This endpoint requires Confluent Kafka which has been removed for Datadog-only submission"
    })
    await websocket.close()


