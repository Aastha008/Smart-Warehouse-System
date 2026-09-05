"""
AI Warehouse Intelligence - Risk Explanation Generator

Generates human-readable explanations for detected events.
Never claims definite damage - uses "potential damage-causing event" language.
"""
from typing import Dict, Any


def generate_explanation(event_type: str, evidence: Dict[str, Any], risk_level: str) -> str:
    """
    Generate a human-readable explanation for a detected behaviour event.
    
    Important: Never claims product is definitely damaged. Uses language like:
    - "Potential damage-causing event"
    - "May have resulted in product damage"
    - "Requires inspection to assess impact"
    
    Args:
        event_type: The type of behaviour detected
        evidence: Dictionary of evidence data
        risk_level: The assessed risk level (LOW, MEDIUM, HIGH, CRITICAL)
        
    Returns:
        Human-readable explanation string
    """
    explanations = {
        "product_drop": _explain_drop,
        "product_dragging": _explain_drag,
        "product_throwing": _explain_throw,
        "rough_handling": _explain_rough,
        "improper_stacking": _explain_stacking,
        "unstable_stacking": _explain_unstable,
        "product_outside_zone": _explain_zone,
        "incorrect_pallet_position": _explain_pallet,
        "unsafe_loading_sequence": _explain_loading,
        "improper_handling_equipment": _explain_equipment,
    }

    handler = explanations.get(event_type, _explain_generic)
    return handler(evidence, risk_level)


def _explain_drop(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain a product drop event."""
    parts = ["Box slipped or fell from handling height directly onto the concrete dock floor."]

    drop_height = evidence.get("drop_height_px", 0)
    drop_m = evidence.get("drop_height_m")
    if drop_m:
        parts.append(f"Estimated fall height: ~{drop_m:.1f} meters.")
    elif drop_height > 0:
        est_m = min(2.0, max(0.5, round(drop_height / 120.0, 1)))
        parts.append(f"Estimated fall height: ~{est_m}m above floor level.")

    if risk_level in ("HIGH", "CRITICAL"):
        parts.append("Impact was sudden and exceeded safe handling limits.")
        parts.append("Potential damage-causing event: please inspect outer box and internal contents before staging.")
    else:
        parts.append("Minor drop observed. Check corner seals before loading onto pallets.")

    return " ".join(parts)


def _explain_drag(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain a product dragging event."""
    dist_m = evidence.get("distance_m")
    drag_dist = evidence.get("drag_distance_px", 0)
    
    if dist_m:
        dist_str = f"for ~{dist_m:.1f} meters"
    elif drag_dist > 0:
        dist_str = f"for ~{max(1, round(drag_dist / 40.0))} meters"
    else:
        dist_str = "across the floor"

    parts = [
        f"Carton was dragged along the concrete floor {dist_str} rather than transferred with a hand truck or pallet jack.",
        "Abrasive floor friction can wear through bottom cardboard, damage barcodes, and tear shipping labels.",
        "Use a two-wheel dolly or pallet truck for transit."
    ]
    return " ".join(parts)


def _explain_throw(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain a product throwing event."""
    parts = [
        "Package was tossed across the handling area rather than handed off in a controlled, two-person transfer.",
        "High-velocity airborne release creates severe impact force on landing, risking broken contents and torn packaging.",
        "Urgent safety review: remind team members that throwing parcels is strictly prohibited."
    ]
    return " ".join(parts)


def _explain_rough(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain rough handling."""
    parts = [
        "Box was handled abruptly with sharp jolts and sudden impacts.",
        "Rough handling or slamming packages against dock plates risks shifting internal contents, rupturing liquid containers, and crushing corner seams."
    ]
    return " ".join(parts)


def _explain_stacking(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain improper stacking."""
    parts = [
        "Stack configuration violates heavy-on-bottom rules: a heavier or wider box is resting on top of a smaller base carton."
    ]
    if evidence.get("overhang_fraction", 0) > 0 or evidence.get("overhang_ratio", 0) > 0:
        parts.append("Top carton noticeably overhangs the lower tier edge, creating uneven downward pressure.")
    parts.append("This creates an unstable center of gravity and risks crushing the lower package.")
    return " ".join(parts)


def _explain_unstable(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain unstable stacking."""
    parts = [
        "Pallet stack is visibly leaning and wobbling beyond safe vertical tolerance.",
        "The stack height and tilt angle make this load prone to toppling over when moved by forklift or hand jack.",
        "Halt transit and restack the upper tiers before moving."
    ]
    return " ".join(parts)


def _explain_zone(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain product outside zone."""
    parts = [
        "Cargo was set down outside the designated yellow dock boundary line.",
        "Boxes left in thoroughfares obstruct forklift transit lanes and create pedestrian trip hazards.",
        "Move cargo into marked bay holding squares."
    ]
    return " ".join(parts)


def _explain_pallet(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain incorrect pallet position."""
    parts = [
        "Pallet is misaligned and freight extends beyond the timber pallet runners into the forklift transit aisle.",
        "Overhanging corners risk snagging on adjacent cargo or being struck by passing equipment.",
        "Square up the pallet inside floor perimeter lines."
    ]
    return " ".join(parts)


def _explain_loading(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain unsafe loading sequence."""
    parts = [
        "Unsafe loading sequence detected in dock area.",
        "Multiple operators moving heavy freight simultaneously within tight quarters without adequate safety clearance.",
        "Sequence the loading flow so one operator clears the trailer before the next load enters."
    ]
    return " ".join(parts)


def _explain_equipment(evidence: Dict[str, Any], risk_level: str) -> str:
    """Explain improper handling equipment."""
    parts = [
        "Heavy or bulky freight was lifted manually without appropriate handling gear nearby.",
        "Manual handling of overweight items risks employee strain and dropped cargo.",
        "Utilize a hydraulic pallet jack, forklift, or two-person team lift."
    ]
    return " ".join(parts)


def _explain_generic(evidence: Dict[str, Any], risk_level: str) -> str:
    """Generic explanation for unknown event types."""
    return (
        f"Handling caution flagged at risk level: {risk_level}. "
        "Dock supervisor review recommended to ensure cargo was staged safely."
    )


def generate_recommendation(event_type: str) -> str:
    """
    Generate actionable recommendation for a detected event.
    
    Args:
        event_type: The type of behaviour detected
        
    Returns:
        Recommendation string
    """
    recommendations = {
        "product_drop": (
            "Inspect the product for potential damage. "
            "Review unloading procedure with the team. "
            "Ensure products are placed with controlled movements, not dropped."
        ),
        "product_dragging": (
            "Provide appropriate transport equipment (trolley, pallet truck). "
            "Schedule handling refresher training. "
            "Products should be lifted and carried, not dragged."
        ),
        "product_throwing": (
            "Immediately inspect the product for damage. "
            "Review loading procedures urgently. "
            "Investigate if workload or time pressure is contributing. "
            "Throwing products is never acceptable."
        ),
        "rough_handling": (
            "Review handling technique with the operator. "
            "Check if time pressure or fatigue is a factor. "
            "Ensure adequate staffing for the current workload."
        ),
        "improper_stacking": (
            "Rearrange the stack with heavy items at the base. "
            "Review stacking protocol with the team. "
            "Ensure stacking guidelines are clearly posted."
        ),
        "unstable_stacking": (
            "Stabilize the stack immediately to prevent toppling. "
            "Reduce stack height. Consider additional pallets. "
            "Verify load stability before leaving unattended."
        ),
        "product_outside_zone": (
            "Relocate the product to the designated zone. "
            "Review zone markings for visibility. "
            "Ensure operators know the designated placement areas."
        ),
        "incorrect_pallet_position": (
            "Realign the pallet to the correct position. "
            "Check floor markings for clarity. "
            "Verify all products are within pallet boundaries."
        ),
        "unsafe_loading_sequence": (
            "Pause loading and review the sequence. "
            "Ensure only one operator loads at a time when space is limited. "
            "Follow the established loading checklist."
        ),
        "improper_handling_equipment": (
            "Provide appropriate handling equipment before proceeding. "
            "Do not manually move items that require mechanical assistance. "
            "Review equipment availability at this station."
        ),
    }

    return recommendations.get(event_type, (
        "Review the handling procedure and inspect the product. "
        "Consult with the warehouse supervisor for guidance."
    ))
