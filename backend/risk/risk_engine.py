"""
AI Warehouse Intelligence - Risk Scoring Engine

Implements configurable multi-factor risk scoring with 4 levels:
LOW (0-30), MEDIUM (31-60), HIGH (61-85), CRITICAL (86-100)

Risk Score = Base Score + Σ(Modifiers) * Confidence
"""
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from backend.behaviour.base_detector import BehaviourEvent
from backend.risk.risk_explanation import generate_explanation, generate_recommendation


@dataclass
class RiskAssessment:
    """Structured risk assessment for a behaviour event."""
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    score: int  # 0-100
    explanation: str
    recommendation: str
    modifiers_applied: dict = field(default_factory=dict)


class RiskEngine:
    """
    Configurable risk scoring engine.
    
    Loads base scores and modifiers from configs/risk.yaml.
    Computes multi-factor risk scores for detected behaviour events.
    """

    def __init__(self, config_path: str = "configs/risk.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

        # Base risk scores by behaviour type
        self.base_scores = self.config.get("base_scores", {
            "product_drop": 70,
            "product_throwing": 85,
            "product_dragging": 50,
            "rough_handling": 65,
            "improper_stacking": 60,
            "unstable_stacking": 75,
            "product_outside_zone": 40,
            "incorrect_pallet_position": 55,
            "unsafe_loading_sequence": 70,
            "improper_handling_equipment": 45,
        })

        # Risk level thresholds
        self.levels = self.config.get("levels", {
            "LOW": {"min_score": 0, "max_score": 30},
            "MEDIUM": {"min_score": 31, "max_score": 60},
            "HIGH": {"min_score": 61, "max_score": 85},
            "CRITICAL": {"min_score": 86, "max_score": 100},
        })

        # Modifiers
        self.modifiers = self.config.get("modifiers", {})

    def _load_config(self) -> Dict[str, Any]:
        """Load risk configuration from YAML."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def classify_risk(self, event: BehaviourEvent,
                      extra_modifiers: Optional[Dict[str, str]] = None) -> RiskAssessment:
        """
        Classify risk for a behaviour event.

        Args:
            event: The detected behaviour event
            extra_modifiers: Optional additional modifiers (product_type, repeat_offence, etc.)

        Returns:
            RiskAssessment with level, score, explanation, and recommendation
        """
        # Start with base score
        base_score = self.base_scores.get(event.event_type, 50)

        # Apply modifiers
        modifier_total = 0
        modifiers_applied = {}

        evidence = event.evidence or {}
        extra = extra_modifiers or {}

        # Drop height modifier
        if "drop_height_px" in evidence:
            height = evidence["drop_height_px"]
            if height > 150:
                mod = self.modifiers.get("drop_height", {}).get("high", 20)
                modifier_total += mod
                modifiers_applied["drop_height"] = f"+{mod} (high: {height}px)"
            elif height > 80:
                mod = self.modifiers.get("drop_height", {}).get("medium", 10)
                modifier_total += mod
                modifiers_applied["drop_height"] = f"+{mod} (medium: {height}px)"

        # Velocity modifier
        if "velocity" in evidence:
            vel = abs(evidence["velocity"])
            if vel > 6.0:
                mod = self.modifiers.get("velocity", {}).get("high", 15)
                modifier_total += mod
                modifiers_applied["velocity"] = f"+{mod} (high: {vel:.1f})"
            elif vel > 3.0:
                mod = self.modifiers.get("velocity", {}).get("medium", 5)
                modifier_total += mod
                modifiers_applied["velocity"] = f"+{mod} (medium: {vel:.1f})"

        # Duration modifier
        duration_s = evidence.get("duration_s") or evidence.get("duration")
        if duration_s is not None:
            if duration_s > 15.0:
                mod = self.modifiers.get("duration", {}).get("extended", 15)
                modifier_total += mod
                modifiers_applied["duration"] = f"+{mod} (extended: {duration_s:.1f}s)"
            elif duration_s > 5.0:
                mod = self.modifiers.get("duration", {}).get("moderate", 5)
                modifier_total += mod
                modifiers_applied["duration"] = f"+{mod} (moderate: {duration_s:.1f}s)"

        # Equipment modifier
        equipment = extra.get("equipment") or evidence.get("equipment")
        if equipment:
            eq_mod = self.modifiers.get("equipment", {}).get(str(equipment), 0)
            if eq_mod != 0:
                modifier_total += eq_mod
                modifiers_applied["equipment"] = f"+{eq_mod} ({equipment})"

        # Product type modifier
        product_type = extra.get("product_type") or evidence.get("product_type", "standard")
        pt_mod = self.modifiers.get("product_type", {}).get(product_type, 0)
        if pt_mod != 0:
            modifier_total += pt_mod
            modifiers_applied["product_type"] = f"+{pt_mod} ({product_type})"

        # Repeat offence modifier
        repeat = extra.get("repeat_offence", "first")
        rp_mod = self.modifiers.get("repeat_offence", {}).get(repeat, 0)
        if rp_mod != 0:
            modifier_total += rp_mod
            modifiers_applied["repeat_offence"] = f"+{rp_mod} ({repeat})"

        # Location modifier
        location = extra.get("location_type") or extra.get("location") or evidence.get("location", "storage_area")
        loc_mod = self.modifiers.get("location", {}).get(location, 0)
        if loc_mod != 0:
            modifier_total += loc_mod
            modifiers_applied["location"] = f"+{loc_mod} ({location})"

        # Confidence scaling - higher confidence = higher effective risk
        confidence_factor = max(0.5, min(1.0, event.confidence if event.confidence is not None else 0.5))

        # Calculate final score
        raw_score = base_score + modifier_total
        final_score = int(raw_score * confidence_factor)
        final_score = max(0, min(100, final_score))  # Clamp to 0-100

        # Determine risk level
        level = self._score_to_level(final_score)

        # Generate explanation and recommendation
        explanation = generate_explanation(event.event_type, evidence, level)
        recommendation = generate_recommendation(event.event_type)

        return RiskAssessment(
            level=level,
            score=final_score,
            explanation=explanation,
            recommendation=recommendation,
            modifiers_applied=modifiers_applied,
        )

    def calculate_composite_risk(self, base_score: float, modifiers: Dict[str, float], confidence: float = 1.0) -> int:
        """Calculate composite risk score given numeric values."""
        raw = base_score + sum(modifiers.values())
        score = int(raw * max(0.5, min(1.0, confidence)))
        return max(0, min(100, score))

    def assess_risk(self, event_type: str, evidence: Dict[str, Any],
                    modifiers: Optional[Dict[str, str]] = None) -> RiskAssessment:
        """
        Alternative interface for risk assessment without a full BehaviourEvent.

        Args:
            event_type: The type of behaviour (e.g., "product_drop")
            evidence: Evidence dictionary
            modifiers: Optional modifiers dict

        Returns:
            RiskAssessment
        """
        # Create a temporary event
        event = BehaviourEvent(
            event_type=event_type,
            object_id=0,
            frame_idx=0,
            confidence=0.85,  # Default confidence
            evidence=evidence,
        )
        return self.classify_risk(event, modifiers)

    def _score_to_level(self, score: int) -> str:
        """Convert numeric score to risk level string."""
        if score >= 86:
            return "CRITICAL"
        elif score >= 61:
            return "HIGH"
        elif score >= 31:
            return "MEDIUM"
        else:
            return "LOW"

    def get_action_for_level(self, level: str) -> str:
        """Get recommended action type for a risk level."""
        actions = {
            "LOW": "log",
            "MEDIUM": "notify",
            "HIGH": "alert",
            "CRITICAL": "intervene",
        }
        return actions.get(level, "log")

    def get_color_for_level(self, level: str) -> str:
        """Get display color for risk level."""
        colors = {
            "LOW": "#22c55e",
            "MEDIUM": "#f59e0b",
            "HIGH": "#f97316",
            "CRITICAL": "#ef4444",
        }
        return colors.get(level, "#6b7280")

    def get_icon_for_level(self, level: str) -> str:
        """Get icon for risk level."""
        icons = {
            "LOW": "🟢",
            "MEDIUM": "🟡",
            "HIGH": "🟠",
            "CRITICAL": "🔴",
        }
        return icons.get(level, "⚪")
