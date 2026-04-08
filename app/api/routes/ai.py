from fastapi import APIRouter, HTTPException
from app.schemas.ai import (
    ChatRequest, ChatResponse,
    DailyTipRequest, DailyTipResponse,
    WeeklyReviewRequest, WeeklyReviewResponse,
    MicroGoalsRequest, MicroGoalsResponse
)
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI Features"])

@router.post("/chat", response_model=ChatResponse)
async def ai_coach_chat(request: ChatRequest):
    try:
        reply = await ai_service.generate_chat_reply(request)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/daily-tip", response_model=DailyTipResponse)
async def get_daily_tip(request: DailyTipRequest):
    try:
        return await ai_service.generate_daily_tip(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weekly-review", response_model=WeeklyReviewResponse)
async def get_weekly_review(request: WeeklyReviewRequest):
    try:
        return await ai_service.generate_weekly_review(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/micro-goals", response_model=MicroGoalsResponse)
async def get_micro_goals(request: MicroGoalsRequest):
    try:
        return await ai_service.generate_micro_goals(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
