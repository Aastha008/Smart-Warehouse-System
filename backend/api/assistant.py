"""AI Assistant API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.assistant import AssistantQuery, AssistantResponse
from backend.assistant.assistant import WarehouseAssistant
from backend.database.connection import get_db
from backend.services.event_service import EventService

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
assistant_svc = WarehouseAssistant()


@router.post("/query", response_model=AssistantResponse)
async def query_assistant(req: AssistantQuery, db: AsyncSession = Depends(get_db)):
    """Process a natural language query from the warehouse supervisor."""
    # Get real data to ground the assistant's response
    try:
        stats = await EventService.get_statistics(db)
        events = await EventService.get_events(db, limit=20)
        events_data = [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "risk_level": e.risk_level,
                "confidence": e.confidence,
                "location": e.location,
                "timestamp": str(e.timestamp),
                "explanation": e.explanation,
            }
            for e in events
        ]
    except Exception:
        stats = None
        events_data = None

    result = assistant_svc.process_query(
        query=req.query,
        events_data=events_data,
        stats_data=stats,
    )
    return AssistantResponse(**result)
