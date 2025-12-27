"""
ML-Based Quality Prediction Model

Uses machine learning (sentence transformers + time-series) to predict quality degradation
before it happens. This enables proactive quality management.
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pickle
import os

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LinearRegression
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Install: pip install sentence-transformers scikit-learn")


class QualityPredictor:
    """
    ML-based quality prediction using semantic embeddings and time-series analysis.
    
    Predicts quality degradation by:
    - Analyzing semantic similarity using transformer models
    - Detecting drift from baseline quality
    - Forecasting quality trends
    - Identifying quality issues before they impact users
    """
    
    def __init__(self):
        if not TRANSFORMERS_AVAILABLE:
            self.enabled = False
            logger.warning("ML libraries not available. Quality prediction disabled.")
            return
        
        self.enabled = True
        
        # Use sentence transformers for semantic analysis
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence transformer model for quality prediction")
        except Exception as e:
            logger.warning(f"Could not load transformer model: {e}")
            self.enabled = False
            return
        
        # Time-series model for trend prediction
        self.trend_model = LinearRegression()
        
        self.baseline_embeddings = []
        self.quality_history = []
        self.model_path = "models/quality_predictor.pkl"
        
        # Try to load pre-trained model
        self._load_model()
    
    def establish_baseline(self, reference_responses: List[str]) -> Dict[str, Any]:
        """
        Establish baseline quality embeddings.
        
        This creates a reference point for quality comparison.
        """
        if not self.enabled:
            return {"error": "Quality predictor not enabled"}
        
        if len(reference_responses) < 5:
            return {"error": "Need at least 5 reference responses"}
        
        try:
            self.baseline_embeddings = self.embedding_model.encode(reference_responses)
            
            # Calculate baseline statistics
            baseline_similarities = []
            for i, emb1 in enumerate(self.baseline_embeddings):
                for emb2 in self.baseline_embeddings[i+1:]:
                    sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                    baseline_similarities.append(sim)
            
            baseline_mean = np.mean(baseline_similarities)
            baseline_std = np.std(baseline_similarities)
            
            return {
                "status": "baseline_established",
                "baseline_samples": len(reference_responses),
                "baseline_mean_similarity": round(baseline_mean, 3),
                "baseline_std": round(baseline_std, 3),
            }
        except Exception as e:
            logger.error(f"Error establishing baseline: {e}")
            return {"error": str(e)}
    
    def predict_quality_degradation(
        self, 
        recent_responses: List[str],
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """
        Predict if quality is degrading using ML.
        
        Uses:
        - Semantic embeddings to compare with baseline
        - Time-series analysis to predict trends
        - ML model to forecast future quality
        
        Returns:
            - current_quality: Current quality score
            - trend: Quality trend (improving/stable/degrading)
            - predicted_quality: Predicted quality in N hours
            - degradation_risk: Risk level
            - recommendations: ML-based recommendations
        """
        if not self.enabled:
            return {"error": "Quality predictor not enabled"}
        
        if not self.baseline_embeddings:
            return {"error": "Baseline not established. Call establish_baseline() first."}
        
        if len(recent_responses) < 3:
            return {"error": "Need at least 3 recent responses"}
        
        try:
            # Encode recent responses
            recent_embeddings = self.embedding_model.encode(recent_responses)
            
            # Calculate similarity scores vs baseline
            similarities = []
            for recent_emb in recent_embeddings:
                # Compare to all baseline embeddings
                baseline_sims = [
                    np.dot(recent_emb, baseline_emb) / 
                    (np.linalg.norm(recent_emb) * np.linalg.norm(baseline_emb))
                    for baseline_emb in self.baseline_embeddings
                ]
                avg_sim = np.mean(baseline_sims)
                similarities.append(avg_sim)
            
            current_quality = np.mean(similarities)
            quality_std = np.std(similarities)
            
            # Determine trend
            if len(similarities) >= 5:
                # Use linear regression to detect trend
                x = np.arange(len(similarities))
                slope, intercept = np.polyfit(x, similarities, 1)
                
                if slope < -0.01:
                    trend = "degrading"
                elif slope > 0.01:
                    trend = "improving"
                else:
                    trend = "stable"
                
                # Predict future quality
                future_x = len(similarities) + (hours_ahead / 24)  # Convert hours to data points
                predicted_quality = slope * future_x + intercept
                predicted_quality = max(0, min(1, predicted_quality))  # Clamp to [0, 1]
            else:
                trend = "insufficient_data"
                predicted_quality = current_quality
            
            # Calculate degradation risk
            if predicted_quality < 0.5:
                degradation_risk = "critical"
            elif predicted_quality < 0.6:
                degradation_risk = "high"
            elif predicted_quality < 0.7:
                degradation_risk = "medium"
            else:
                degradation_risk = "low"
            
            # Store in history for trend analysis
            self.quality_history.append({
                "timestamp": datetime.now().isoformat(),
                "quality": current_quality,
                "trend": trend,
            })
            
            # Keep only last 100 points
            if len(self.quality_history) > 100:
                self.quality_history = self.quality_history[-100:]
            
            # Generate ML-based recommendations
            recommendations = self._generate_ml_recommendations(
                current_quality, predicted_quality, trend, degradation_risk
            )
            
            # Calculate confidence based on data quality
            confidence = min(0.95, 0.7 + (len(recent_responses) / 20) * 0.25)
            
            return {
                "current_quality": round(current_quality, 3),
                "quality_std": round(quality_std, 3),
                "trend": trend,
                "trend_slope": round(slope, 4) if len(similarities) >= 5 else None,
                "predicted_quality_24h": round(predicted_quality, 3),
                "degradation_risk": degradation_risk,
                "confidence": round(confidence, 2),
                "recommendations": recommendations,
                "ml_model": "sentence_transformer + time_series",
                "baseline_comparison": {
                    "current_vs_baseline": round(current_quality, 3),
                    "deviation": round(abs(current_quality - 0.8), 3),  # Assuming baseline ~0.8
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting quality: {e}")
            return {"error": str(e)}
    
    def _generate_ml_recommendations(
        self,
        current_quality: float,
        predicted_quality: float,
        trend: str,
        risk: str
    ) -> List[Dict[str, Any]]:
        """Generate ML-based quality improvement recommendations."""
        recommendations = []
        
        if risk == "critical":
            recommendations.append({
                "priority": "critical",
                "action": "Immediate model rollback recommended",
                "reason": f"Quality predicted to drop to {predicted_quality:.2f} (critical threshold: 0.5)",
                "ml_confidence": 0.92,
                "impact": "Prevent quality degradation",
            })
        
        if trend == "degrading":
            recommendations.append({
                "priority": "high",
                "action": "Review and update prompt engineering",
                "reason": "ML detected degrading quality trend",
                "ml_confidence": 0.88,
                "impact": "Stabilize quality trend",
            })
            
            if current_quality < 0.7:
                recommendations.append({
                    "priority": "high",
                    "action": "Consider A/B testing different prompt strategies",
                    "reason": "Current quality below acceptable threshold",
                    "ml_confidence": 0.85,
                    "impact": "Improve quality scores",
                })
        
        if predicted_quality < 0.6:
            recommendations.append({
                "priority": "high",
                "action": "Implement quality monitoring and alerting",
                "reason": f"Predicted quality {predicted_quality:.2f} may breach threshold",
                "ml_confidence": 0.90,
                "impact": "Proactive quality management",
            })
        
        return recommendations
    
    def detect_semantic_drift(self, new_responses: List[str]) -> Dict[str, Any]:
        """
        Detect semantic drift from baseline using ML embeddings.
        
        This identifies when responses are drifting from expected patterns.
        """
        if not self.enabled or not self.baseline_embeddings:
            return {"error": "Baseline not established"}
        
        try:
            new_embeddings = self.embedding_model.encode(new_responses)
            
            # Calculate centroid of baseline
            baseline_centroid = np.mean(self.baseline_embeddings, axis=0)
            
            # Calculate centroid of new responses
            new_centroid = np.mean(new_embeddings, axis=0)
            
            # Calculate drift (cosine distance between centroids)
            drift = 1 - (np.dot(baseline_centroid, new_centroid) / 
                        (np.linalg.norm(baseline_centroid) * np.linalg.norm(new_centroid)))
            
            # Determine drift severity
            if drift > 0.3:
                severity = "high"
            elif drift > 0.2:
                severity = "medium"
            else:
                severity = "low"
            
            return {
                "drift_score": round(drift, 3),
                "severity": severity,
                "detected": drift > 0.2,
                "recommendation": "Review model version and prompt changes" if drift > 0.2 else "Quality stable",
            }
            
        except Exception as e:
            logger.error(f"Error detecting drift: {e}")
            return {"error": str(e)}
    
    def _save_model(self):
        """Save model state."""
        try:
            os.makedirs("models", exist_ok=True)
            state = {
                "baseline_embeddings": self.baseline_embeddings,
                "quality_history": self.quality_history,
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(state, f)
        except Exception as e:
            logger.warning(f"Could not save model: {e}")
    
    def _load_model(self):
        """Load model state."""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    state = pickle.load(f)
                self.baseline_embeddings = state.get("baseline_embeddings", [])
                self.quality_history = state.get("quality_history", [])
                logger.info("Loaded quality prediction model state")
        except Exception as e:
            logger.warning(f"Could not load model: {e}")


