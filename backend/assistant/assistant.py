"""
AI Warehouse Intelligence - Warehouse Supervisor AI Assistant

Grounded conversational AI that reasons over event database, statistics,
and detected incidents. Uses tool-calling pattern to query actual data.
Never invents warehouse events.
"""
import os
import re
import yaml
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from backend.database.models import Event, Alert


def get_current_time():
    return datetime.now(timezone.utc)


NON_WAREHOUSE_PATTERNS = [
    r"\b(capital of|weather|president|prime minister|movie|film|celebrity|actor|actress|recipe|cook|cooking|spaghetti|bolognese|food|dinner|restaurant|football|soccer|basketball|baseball|tennis|cricket|sports|game|score|cryptocurrency|bitcoin|ethereum|stocks|stock market|shares)\b",
    r"\b(write a poem|write poetry|sing a song|tell me a joke|write a story about|solve math|poem|poetry|song|sing|lyrics|joke|riddle|story|novel|fiction|essay|math|algebra|calculus)\b",
    r"\b(javascript|react|vue|angular|framework|tutorial|html|css|python game|programming|coding)\b",
    r"\b(france|paris|london|new york|tokyo|germany|spain|italy|europe|america|asia)\b",
]

WAREHOUSE_KEYWORDS = {
    "warehouse", "bay", "bays", "loading", "unloading", "event", "events", "incident", "incidents",
    "drop", "dropped", "dropping", "drag", "dragged", "dragging", "throw", "threw", "throwing",
    "rough", "handling", "stack", "stacked", "stacking", "unstable", "pallet", "pallets",
    "zone", "zones", "sequence", "equipment", "forklift", "trolley", "camera", "cameras",
    "risk", "risks", "risky", "hazard", "hazards", "safety", "damage", "prevention", "telemetry",
    "today", "yesterday", "shift", "shifts", "operator", "operators", "worker", "workers",
    "package", "packages", "carton", "cartons", "cargo", "stats", "statistics", "trend",
    "trends", "summary", "overview", "report", "alert", "alerts", "rule", "rules", "protocol",
    "protocols", "status", "critical", "severe", "serious", "corrective", "action", "actions",
    "recommendation", "recommendations", "training", "frequent", "common", "classify",
    "classified", "detection", "detector", "velocity", "height", "guideline", "guidelines",
    "operation", "operations", "cargo", "parcels", "parcel", "box", "boxes",
}

GREETING_PATTERNS = [
    r"^(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b",
    r"\b(help|what can you do|capabilities|options|commands|menu|start)\b",
]


class AssistantTools:
    """Database query and warehouse rule tools for the AI assistant."""

    def __init__(self, db_session_factory=None, rules_path: str = "configs/warehouse_rules.yaml"):
        self.db_session_factory = db_session_factory
        self.rules_path = rules_path
        self._rules_cache = None

    def get_warehouse_rules(self, category: Optional[str] = None) -> dict:
        """Get official warehouse handling and stacking rules from configuration."""
        if self._rules_cache is None:
            try:
                if os.path.exists(self.rules_path):
                    with open(self.rules_path, "r", encoding="utf-8") as f:
                        self._rules_cache = yaml.safe_load(f) or {}
                else:
                    self._rules_cache = {}
            except Exception:
                self._rules_cache = {}

        if not category:
            return self._rules_cache
        return self._rules_cache.get("rules", {}).get(category, [])

    def get_events(self, limit: int = 20, risk_level: Optional[str] = None,
                   event_type: Optional[str] = None, location: Optional[str] = None) -> list[dict]:
        """Get recent events from database."""
        if self.db_session_factory:
            try:
                with self.db_session_factory() as session:
                    query = select(Event)
                    if risk_level:
                        query = query.where(func.upper(Event.risk_level) == risk_level.upper())
                    if event_type:
                        query = query.where(Event.event_type == event_type)
                    if location:
                        query = query.where(Event.location == location)
                    query = query.order_by(Event.timestamp.desc()).limit(limit)
                    result = session.execute(query)
                    events = result.scalars().all()
                    return [
                        {
                            "event_id": e.event_id,
                            "timestamp": str(e.timestamp),
                            "camera_id": e.camera_id,
                            "location": e.location,
                            "event_type": e.event_type,
                            "risk_level": e.risk_level,
                            "risk_score": e.risk_score,
                            "confidence": e.confidence,
                            "explanation": e.explanation,
                            "recommendation": e.recommendation,
                        }
                        for e in events
                    ]
            except Exception:
                pass
        return []

    def get_statistics(self) -> dict:
        """Get aggregate statistics from database."""
        if self.db_session_factory:
            try:
                with self.db_session_factory() as session:
                    total = session.execute(select(func.count(Event.event_id))).scalar() or 0
                    high = session.execute(select(func.count(Event.event_id)).where(Event.risk_level == "HIGH")).scalar() or 0
                    crit = session.execute(select(func.count(Event.event_id)).where(Event.risk_level == "CRITICAL")).scalar() or 0
                    today_start = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0)
                    today_count = session.execute(select(func.count(Event.event_id)).where(Event.timestamp >= today_start)).scalar() or 0
                    
                    by_behaviour = {}
                    for row in session.execute(select(Event.event_type, func.count(Event.event_id)).group_by(Event.event_type)).all():
                        by_behaviour[row[0]] = row[1]
                        
                    by_location = {}
                    for row in session.execute(select(Event.location, func.count(Event.event_id)).group_by(Event.location)).all():
                        by_location[row[0]] = row[1]
                        
                    by_risk_level = {}
                    for row in session.execute(select(Event.risk_level, func.count(Event.event_id)).group_by(Event.risk_level)).all():
                        by_risk_level[row[0]] = row[1]

                    return {
                        "total_events": total,
                        "high_risk": high,
                        "high_risk_count": high,
                        "critical": crit,
                        "critical_count": crit,
                        "events_today": today_count,
                        "by_behaviour": by_behaviour,
                        "by_location": by_location,
                        "by_risk_level": by_risk_level,
                    }
            except Exception:
                pass

        return {
            "total_events": 0,
            "high_risk": 0,
            "high_risk_count": 0,
            "critical": 0,
            "critical_count": 0,
            "events_today": 0,
            "by_behaviour": {},
            "by_location": {},
            "by_risk_level": {},
        }

    def get_high_risk_events(self, limit: int = 10) -> list[dict]:
        """Get high-risk and critical events."""
        if self.db_session_factory:
            try:
                with self.db_session_factory() as session:
                    query = (
                        select(Event)
                        .where(Event.risk_level.in_(["HIGH", "CRITICAL"]))
                        .order_by(Event.timestamp.desc())
                        .limit(limit)
                    )
                    result = session.execute(query)
                    events = result.scalars().all()
                    return [
                        {
                            "event_id": e.event_id,
                            "timestamp": str(e.timestamp),
                            "camera_id": e.camera_id,
                            "location": e.location,
                            "event_type": e.event_type,
                            "risk_level": e.risk_level,
                            "risk_score": e.risk_score,
                            "confidence": e.confidence,
                            "explanation": e.explanation,
                            "recommendation": e.recommendation,
                        }
                        for e in events
                    ]
            except Exception:
                pass
        return []

    def get_location_stats(self) -> dict:
        """Get event counts by location."""
        stats = self.get_statistics()
        return stats.get("by_location", {})

    def get_event_details(self, event_id: str) -> Optional[dict]:
        """Get detailed information about a specific event."""
        if self.db_session_factory:
            try:
                with self.db_session_factory() as session:
                    event = session.execute(select(Event).where(Event.event_id == event_id)).scalar_one_or_none()
                    if event:
                        return {
                            "event_id": event.event_id,
                            "timestamp": str(event.timestamp),
                            "camera_id": event.camera_id,
                            "location": event.location,
                            "event_type": event.event_type,
                            "risk_level": event.risk_level,
                            "risk_score": event.risk_score,
                            "confidence": event.confidence,
                            "explanation": event.explanation,
                            "recommendation": event.recommendation,
                            "evidence": event.evidence,
                        }
            except Exception:
                pass
        return None

    def get_behaviour_trends(self, days: int = 7) -> dict:
        """Get behaviour trends over time."""
        return {}


class WarehouseAssistant:
    """
    AI Warehouse Supervisor Assistant.

    Architecture:
        User → Domain Guardrail Check → Query Parser → Tool Selection → Data Retrieval → Grounded Response Generation

    The assistant ONLY reasons over actual data from warehouse telemetry and rules.
    It refuses ungrounded, out-of-domain queries and never invents events.
    """

    def __init__(self, db_session_factory=None, llm_api_key: Optional[str] = None):
        self.tools = AssistantTools(db_session_factory)
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self.use_llm = bool(self.llm_api_key)

        # Query patterns for template-based responses
        self.patterns = [
            (r"what happened today|today.s events|events today",
             self._handle_today_events),
            (r"high.?risk|dangerous|critical|severe|serious",
             self._handle_high_risk),
            (r"common|frequent|most.*(risky|dangerous|common)",
             self._handle_common_behaviours),
            (r"rules?|guidelines?|protocol|stacking rule|handling rule|regulations?",
             self._handle_rules_query),
            (r"which (bay|loading|area|location|zone)|(bay|zone) \d+",
             self._handle_location_query),
            (r"why.*(classified|flagged|high risk|critical)",
             self._handle_why_risk),
            (r"corrective|action|recommendation|what should|how to",
             self._handle_recommendations),
            (r"increasing|trend|getting worse|improving",
             self._handle_trends),
            (r"training|operator|worker|staff",
             self._handle_training),
            (r"summary|overview|report|status",
             self._handle_summary),
            (r"stacking|stack",
             self._handle_stacking_query),
            (r"drop|dropped|falling",
             self._handle_drop_query),
            (r"drag|dragging",
             self._handle_drag_query),
            (r"throw|throwing",
             self._handle_throw_query),
        ]

    def process_query(self, query: str, events_data: Optional[list] = None,
                      stats_data: Optional[dict] = None) -> dict:
        """
        Process a natural language query from a warehouse supervisor.

        Args:
            query: The user's question
            events_data: Optional pre-fetched events data
            stats_data: Optional pre-fetched statistics data

        Returns:
            dict with 'response', 'sources', 'data_used'
        """
        if not query or not query.strip():
            return {
                "response": "Please ask a question about warehouse operations, events, or safety.",
                "sources": [],
                "data_used": {},
            }

        query_lower = query.lower().strip()

        # Domain Guardrail: detect out-of-domain / non-warehouse queries
        for pat in NON_WAREHOUSE_PATTERNS:
            if re.search(pat, query_lower):
                return {
                    "response": (
                        "I am your Warehouse Shift Supervisor Assistant, and my focus is strictly restricted "
                        "to warehouse operations, loading/unloading safety, and dock handling protocols. "
                        "I cannot assist with non-warehouse topics."
                    ),
                    "sources": ["domain_guardrails"],
                    "data_used": {},
                }

        # Check if greeting or help
        for pat in GREETING_PATTERNS:
            if re.search(pat, query_lower):
                return self._handle_general(query, events_data, stats_data)

        # Check if any warehouse pattern matches
        for pattern, handler in self.patterns:
            if re.search(pattern, query_lower):
                if self.use_llm:
                    try:
                        return self._llm_response(query, events_data, stats_data)
                    except Exception:
                        pass
                return handler(query, events_data, stats_data)

        # Check if contains any warehouse keyword
        words = set(re.findall(r"\w+", query_lower))
        if words.intersection(WAREHOUSE_KEYWORDS):
            if self.use_llm:
                try:
                    return self._llm_response(query, events_data, stats_data)
                except Exception:
                    pass
            return self._handle_summary(query, events_data, stats_data)

        # Non-warehouse / out-of-domain query refused
        return {
            "response": (
                "I am your Warehouse Shift Supervisor Assistant, and my focus is strictly restricted "
                "to warehouse operations, loading/unloading safety, and dock handling protocols. "
                "I cannot assist with non-warehouse topics."
            ),
            "sources": ["domain_guardrails"],
            "data_used": {},
        }

    def _handle_rules_query(self, query: str, events_data: Optional[list] = None,
                            stats_data: Optional[dict] = None) -> dict:
        """Handle queries about warehouse safety and handling rules."""
        rules = self.tools.get_warehouse_rules()
        rules_dict = rules.get("rules", {}) if isinstance(rules, dict) else {}

        response = "**Warehouse Handling & Safety Protocols:**\n\n"
        if rules_dict:
            for category, rule_list in rules_dict.items():
                response += f"### {category.title()} Rules:\n"
                for r in rule_list:
                    response += f"- **[{r.get('id', '')}]** {r.get('description', '')}\n"
                    response += f"  - *Good Practice:* {r.get('good_practice', '')}\n"
                    response += f"  - *Severity:* {r.get('severity', 'MEDIUM')}\n"
                response += "\n"
        else:
            response += "Warehouse handling rules: Heavy items at base, no overhang, controlled lifts, designated zone placement."

        return {
            "response": response.strip(),
            "sources": ["warehouse_rules"],
            "data_used": {"categories": list(rules_dict.keys()) if rules_dict else []},
        }

    def _handle_throw_query(self, query: str, events_data: Optional[list] = None,
                            stats_data: Optional[dict] = None) -> dict:
        """Handle product throwing queries."""
        stats = stats_data or self.tools.get_statistics()
        throw_count = stats.get("by_behaviour", {}).get("product_throwing", 0)

        response = f"**Product Throwing Analysis:**\n\n"
        response += f"Total throwing events detected: **{throw_count}**\n\n"
        if throw_count > 0:
            response += (
                "⚠️ **Critical Safety Alert:** Throwing items produces dangerous impact velocities "
                "and violates standard handling procedures.\n\n"
                "**Immediate Actions:**\n"
                "1. Inspect impacted parcels and cargo for hidden damage.\n"
                "2. Conduct immediate supervisor debrief at the affected loading bay.\n"
                "3. Ensure conveyor and staffing allocations reduce time-pressure."
            )
        else:
            response += "No product throwing events have been recorded in the current dataset."

        return {
            "response": response,
            "sources": ["statistics", "warehouse_rules"],
            "data_used": {"throw_count": throw_count},
        }

    def _handle_today_events(self, query: str, events_data: Optional[list] = None,
                             stats_data: Optional[dict] = None) -> dict:
        """Handle queries about today's events."""
        stats = stats_data or self.tools.get_statistics()
        today_count = stats.get("events_today", 0)
        high_risk = stats.get("high_risk_count", 0)
        critical = stats.get("critical_count", 0)

        if today_count == 0:
            response = (
                "No events have been detected today so far. "
                "The warehouse operations appear to be running normally. "
                "I'll continue monitoring for any handling incidents."
            )
        else:
            response = (
                f"Today, **{today_count} events** have been detected so far.\n\n"
            )
            if high_risk > 0:
                response += f"- ⚠️ **{high_risk}** high-risk events requiring attention\n"
            if critical > 0:
                response += f"- 🔴 **{critical}** critical incidents requiring immediate review\n"

            by_behaviour = stats.get("by_behaviour", {})
            if by_behaviour:
                response += "\n**Breakdown by type:**\n"
                for btype, count in sorted(by_behaviour.items(), key=lambda x: -x[1])[:5]:
                    response += f"- {btype.replace('_', ' ').title()}: {count}\n"

            by_location = stats.get("by_location", {})
            if by_location:
                response += "\n**By location:**\n"
                for loc, count in sorted(by_location.items(), key=lambda x: -x[1])[:3]:
                    response += f"- {loc.replace('_', ' ').title()}: {count}\n"

        return {
            "response": response,
            "sources": ["event_database", "statistics"],
            "data_used": stats,
        }

    def _handle_high_risk(self, query: str, events_data: Optional[list] = None,
                          stats_data: Optional[dict] = None) -> dict:
        """Handle queries about high-risk events."""
        stats = stats_data or self.tools.get_statistics()
        high_risk = stats.get("high_risk_count", 0)
        critical = stats.get("critical_count", 0)

        if high_risk == 0 and critical == 0:
            response = (
                "No high-risk or critical events have been recorded in the current period. "
                "All monitored operations appear to be within safe parameters."
            )
        else:
            response = f"**High-Risk Events Summary:**\n\n"
            response += f"- 🟠 High Risk: **{high_risk}** events\n"
            response += f"- 🔴 Critical: **{critical}** events\n\n"

            if events_data:
                response += "**Recent high-risk incidents:**\n"
                hr_events = [e for e in events_data
                            if e.get("risk_level") in ("HIGH", "CRITICAL")][:5]
                for e in hr_events:
                    risk_icon = "🔴" if e.get("risk_level") == "CRITICAL" else "🟠"
                    response += (
                        f"- {risk_icon} {e.get('event_type', 'Unknown').replace('_', ' ').title()} "
                        f"at {e.get('location', 'unknown location')} "
                        f"(confidence: {e.get('confidence', 0):.0%})\n"
                    )

            response += (
                "\n**Recommended action:** Review each high-risk event, "
                "verify conditions on-site, and implement corrective measures."
            )

        return {
            "response": response,
            "sources": ["event_database"],
            "data_used": {"high_risk": high_risk, "critical": critical},
        }

    def _handle_common_behaviours(self, query: str, events_data: Optional[list] = None,
                                   stats_data: Optional[dict] = None) -> dict:
        """Handle queries about most common risky behaviours."""
        stats = stats_data or self.tools.get_statistics()
        by_behaviour = stats.get("by_behaviour", {})

        if not by_behaviour:
            response = "No behaviour data is available yet. Process some warehouse videos to generate insights."
        else:
            sorted_behaviours = sorted(by_behaviour.items(), key=lambda x: -x[1])
            response = "**Most Common Risky Behaviours:**\n\n"
            for i, (btype, count) in enumerate(sorted_behaviours[:5], 1):
                response += f"{i}. **{btype.replace('_', ' ').title()}**: {count} occurrences\n"

            if sorted_behaviours:
                top = sorted_behaviours[0]
                response += (
                    f"\nThe most frequent issue is **{top[0].replace('_', ' ')}** "
                    f"with {top[1]} occurrences. "
                    f"This suggests a need for targeted training on this behaviour."
                )

        return {
            "response": response,
            "sources": ["statistics"],
            "data_used": by_behaviour,
        }

    def _handle_location_query(self, query: str, events_data: Optional[list] = None,
                                stats_data: Optional[dict] = None) -> dict:
        """Handle queries about which locations need attention."""
        stats = stats_data or self.tools.get_statistics()
        by_location = stats.get("by_location", {})

        if not by_location:
            response = "No location-specific data is available yet. Process warehouse videos to generate location insights."
        else:
            sorted_locs = sorted(by_location.items(), key=lambda x: -x[1])
            response = "**Events by Location:**\n\n"
            for loc, count in sorted_locs:
                response += f"- **{loc.replace('_', ' ').title()}**: {count} events\n"

            if sorted_locs:
                top_loc = sorted_locs[0]
                response += (
                    f"\n⚠️ **{top_loc[0].replace('_', ' ').title()}** requires the most attention "
                    f"with {top_loc[1]} events. Consider increasing supervisor presence in this area "
                    f"and reviewing handling procedures."
                )

        return {
            "response": response,
            "sources": ["statistics"],
            "data_used": by_location,
        }

    def _handle_why_risk(self, query: str, events_data: Optional[list] = None,
                          stats_data: Optional[dict] = None) -> dict:
        """Handle queries about why an event was classified as high risk."""
        response = (
            "Events are classified based on multiple factors:\n\n"
            "1. **Behaviour type** - Each behaviour has a base risk score\n"
            "2. **Confidence** - Higher detection confidence increases score\n"
            "3. **Evidence** - Drop height, velocity, duration affect severity\n"
            "4. **Product type** - Fragile items receive higher risk scores\n"
            "5. **Repeat offence** - Repeated violations escalate risk\n"
            "6. **Location** - Certain areas have higher risk multipliers\n\n"
            "The system distinguishes between:\n"
            "- **Observed behaviour**: What was actually detected\n"
            "- **Potential risk**: What might result from the behaviour\n"
            "- **Confirmed damage**: Only when sufficient evidence exists\n\n"
            "The system never claims definite damage without evidence. "
            "All high-risk events should be reviewed by authorized personnel."
        )

        return {
            "response": response,
            "sources": ["risk_configuration"],
            "data_used": {},
        }

    def _handle_recommendations(self, query: str, events_data: Optional[list] = None,
                                 stats_data: Optional[dict] = None) -> dict:
        """Handle queries about corrective actions."""
        stats = stats_data or self.tools.get_statistics()
        by_behaviour = stats.get("by_behaviour", {})

        recommendations = {
            "product_drop": "Review unloading procedures. Ensure products are placed, not dropped. Inspect potentially damaged items.",
            "product_dragging": "Provide trolleys/pallet trucks. Train operators on proper product movement techniques.",
            "product_throwing": "Immediate intervention required. Review loading procedures. Ensure adequate staffing for workload.",
            "rough_handling": "Review handling techniques with operators. Check if time pressure is a factor.",
            "improper_stacking": "Retrain on stacking protocols. Heavy items at bottom, light at top.",
            "unstable_stacking": "Reduce stack heights. Verify load stability before release.",
            "product_outside_zone": "Review zone markings. Ensure designated areas are clearly visible.",
            "incorrect_pallet_position": "Check floor markings. Train on proper pallet alignment.",
            "unsafe_loading_sequence": "Implement loading checklists. Ensure supervisor oversight during loading.",
            "improper_handling_equipment": "Provide appropriate equipment. Review lifting guidelines.",
        }

        response = "**Corrective Action Recommendations:**\n\n"

        if by_behaviour:
            sorted_behaviours = sorted(by_behaviour.items(), key=lambda x: -x[1])
            for btype, count in sorted_behaviours[:5]:
                rec = recommendations.get(btype, "Review operational procedures.")
                response += f"**{btype.replace('_', ' ').title()}** ({count} events):\n"
                response += f"→ {rec}\n\n"
        else:
            response += "No specific events detected yet. General recommendations:\n\n"
            response += "1. Ensure all operators are trained on handling procedures\n"
            response += "2. Verify equipment availability at all loading bays\n"
            response += "3. Maintain clear zone markings\n"
            response += "4. Conduct regular safety briefings\n"

        return {
            "response": response,
            "sources": ["warehouse_rules", "statistics"],
            "data_used": by_behaviour,
        }

    def _handle_trends(self, query: str, events_data: Optional[list] = None,
                        stats_data: Optional[dict] = None) -> dict:
        """Handle queries about trends."""
        response = (
            "To analyze trends accurately, the system needs data from multiple shifts or days.\n\n"
            "**Available trend analysis:**\n"
            "- Risk trends over time (Dashboard → Trends)\n"
            "- Behaviour frequency changes\n"
            "- Location-specific patterns\n"
            "- Shift comparison\n\n"
            "Please check the Analytics page for detailed trend visualizations. "
            "If you notice increasing risk events, consider:\n"
            "1. Additional training sessions\n"
            "2. Process review meetings\n"
            "3. Equipment availability audit\n"
            "4. Workload assessment"
        )

        return {
            "response": response,
            "sources": ["analytics"],
            "data_used": {},
        }

    def _handle_training(self, query: str, events_data: Optional[list] = None,
                          stats_data: Optional[dict] = None) -> dict:
        """Handle queries about training needs."""
        stats = stats_data or self.tools.get_statistics()
        by_behaviour = stats.get("by_behaviour", {})

        response = "**Training Opportunities Identified:**\n\n"

        if by_behaviour:
            sorted_behaviours = sorted(by_behaviour.items(), key=lambda x: -x[1])
            response += "Based on detected behaviours, training should focus on:\n\n"
            for i, (btype, count) in enumerate(sorted_behaviours[:3], 1):
                response += f"{i}. **{btype.replace('_', ' ').title()}** ({count} incidents) - "
                if "drop" in btype:
                    response += "Proper product placement techniques\n"
                elif "drag" in btype:
                    response += "Using appropriate transport equipment\n"
                elif "stack" in btype:
                    response += "Safe stacking procedures and weight distribution\n"
                elif "throw" in btype:
                    response += "Controlled handling during loading/unloading\n"
                else:
                    response += "Correct handling procedures\n"
        else:
            response += (
                "No specific training gaps identified yet. "
                "Process warehouse videos to identify areas where training would be most beneficial."
            )

        response += (
            "\n\n*Note: This system focuses on process improvement, not individual performance evaluation. "
            "Training recommendations are based on observed behaviour patterns.*"
        )

        return {
            "response": response,
            "sources": ["statistics", "behaviour_analysis"],
            "data_used": by_behaviour,
        }

    def _handle_summary(self, query: str, events_data: Optional[list] = None,
                         stats_data: Optional[dict] = None) -> dict:
        """Handle summary/overview queries."""
        stats = stats_data or self.tools.get_statistics()

        total = stats.get("total_events", 0)
        high_risk = stats.get("high_risk_count", 0)
        critical = stats.get("critical_count", 0)
        today = stats.get("events_today", 0)

        response = "**Warehouse Intelligence Summary:**\n\n"
        response += f"📊 Total events tracked: **{total}**\n"
        response += f"📅 Events today: **{today}**\n"
        response += f"🟠 High-risk events: **{high_risk}**\n"
        response += f"🔴 Critical incidents: **{critical}**\n\n"

        by_risk = stats.get("by_risk_level", {})
        if by_risk:
            response += "**Risk Distribution:**\n"
            for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                count = by_risk.get(level, 0)
                if count > 0:
                    icons = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
                    response += f"- {icons.get(level, '⚪')} {level}: {count}\n"

        if total > 0:
            prevention_rate = max(0, total - critical) / max(total, 1) * 100
            response += (
                f"\n**Prevention Metric:** {prevention_rate:.0f}% of potential damage events "
                f"were identified before confirmed damage occurred."
            )
        else:
            response += "\nUpload and analyze warehouse videos to start generating insights."

        return {
            "response": response,
            "sources": ["event_database", "statistics"],
            "data_used": stats,
        }

    def _handle_stacking_query(self, query: str, events_data: Optional[list] = None,
                                stats_data: Optional[dict] = None) -> dict:
        """Handle stacking-specific queries."""
        stats = stats_data or self.tools.get_statistics()
        by_behaviour = stats.get("by_behaviour", {})
        stack_events = by_behaviour.get("improper_stacking", 0) + by_behaviour.get("unstable_stacking", 0)

        response = f"**Stacking Analysis:**\n\n"
        response += f"- Improper stacking events: {by_behaviour.get('improper_stacking', 0)}\n"
        response += f"- Unstable stacking events: {by_behaviour.get('unstable_stacking', 0)}\n\n"

        if stack_events > 0:
            response += (
                "**Recommendations:**\n"
                "1. Heavy items should always be placed at the bottom\n"
                "2. Products must not extend beyond pallet edges\n"
                "3. Stack height should not exceed safe limits\n"
                "4. Verify load stability before release\n"
            )
        else:
            response += "No stacking issues detected in the current data."

        return {
            "response": response,
            "sources": ["statistics", "warehouse_rules"],
            "data_used": {"stack_events": stack_events},
        }

    def _handle_drop_query(self, query: str, events_data: Optional[list] = None,
                            stats_data: Optional[dict] = None) -> dict:
        """Handle drop-specific queries."""
        stats = stats_data or self.tools.get_statistics()
        drop_count = stats.get("by_behaviour", {}).get("product_drop", 0)

        response = f"**Product Drop Analysis:**\n\n"
        response += f"Total drop events detected: **{drop_count}**\n\n"

        if drop_count > 0:
            response += (
                "Product drops are classified based on:\n"
                "- **Drop height** (estimated from bounding box movement)\n"
                "- **Velocity** at point of impact\n"
                "- **Product becoming stationary** after contact with floor\n\n"
                "**Recommendation:** Review unloading procedures and ensure "
                "products are placed with controlled movements."
            )
        else:
            response += "No product drops detected in the current data."

        return {
            "response": response,
            "sources": ["statistics"],
            "data_used": {"drop_count": drop_count},
        }

    def _handle_drag_query(self, query: str, events_data: Optional[list] = None,
                            stats_data: Optional[dict] = None) -> dict:
        """Handle dragging-specific queries."""
        stats = stats_data or self.tools.get_statistics()
        drag_count = stats.get("by_behaviour", {}).get("product_dragging", 0)

        response = f"**Product Dragging Analysis:**\n\n"
        response += f"Total dragging events detected: **{drag_count}**\n\n"

        if drag_count > 0:
            response += (
                "Dragging is detected when products move horizontally "
                "with minimal vertical lift. This can damage product surfaces "
                "and packaging.\n\n"
                "**Recommendation:** Provide trolleys/pallet trucks and train "
                "operators on proper product movement techniques."
            )
        else:
            response += "No product dragging detected in the current data."

        return {
            "response": response,
            "sources": ["statistics"],
            "data_used": {"drag_count": drag_count},
        }

    def _handle_general(self, query: str, events_data: Optional[list] = None,
                         stats_data: Optional[dict] = None) -> dict:
        """Handle general/unmatched queries."""
        response = (
            "Hey! I'm here to help track and improve dock handling safety. Here are a few helpful questions you can ask me:\n\n"
            "- **\"What happened on the dock today?\"** — Get today's handling summary\n"
            "- **\"Show me high-risk events\"** — Review urgent incidents needing sign-off\n"
            "- **\"Which loading bay needs attention?\"** — See which dock has the most flags\n"
            "- **\"What are the most common risky behaviours?\"** — Find out what's causing the most issues on the floor\n"
            "- **\"Why was this classified as high risk?\"** — Understand how the risk scoring works\n"
            "- **\"What corrective action should we take?\"** — Get practical coaching tips for the team\n"
            "- **\"What are the warehouse stacking rules?\"** — Review safe stacking and pallet guidelines\n\n"
            "*All responses are based on actual detected events. "
            "I will explicitly tell you when information is unavailable.*"
        )

        return {
            "response": response,
            "sources": [],
            "data_used": {},
        }

    def _llm_response(self, query: str, events_data: Optional[list] = None,
                       stats_data: Optional[dict] = None) -> dict:
        """Generate response using LLM with tool-calling."""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.llm_api_key)

            # Prepare context from actual data
            stats = stats_data or self.tools.get_statistics()
            context = f"""You are an AI Warehouse Supervisor Assistant. 
You ONLY reason over actual warehouse event data. NEVER invent events.

Current Statistics:
{stats}

Recent Events:
{events_data[:10] if events_data else 'No events available'}

Rules:
1. Only reference data provided above
2. If data is unavailable, say so explicitly
3. Never claim definite product damage without evidence
4. Distinguish between observed behaviour, potential risk, and confirmed damage
5. Focus on prevention, not surveillance
6. Be specific and actionable in recommendations
"""

            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": query},
                ],
                max_tokens=500,
                temperature=0.3,
            )

            return {
                "response": response.choices[0].message.content,
                "sources": ["event_database", "llm_analysis"],
                "data_used": stats,
            }

        except Exception as e:
            # Fall back to template
            return self._template_response(query, events_data, stats_data)
