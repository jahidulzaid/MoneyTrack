from pydantic import BaseModel
from typing import List, Optional

# --- 1. Interactive AI Coach Chat ---
class ChatMessage(BaseModel):
    role: str # 'user', 'assistant'
    content: str

class ChatRequest(BaseModel):
    user_id: int
    messages: List[ChatMessage]
    user_context: Optional[dict] = None

class ChatResponse(BaseModel):
    reply: str

# --- 2. Daily AI Nudges & Tips ---
class CategoryStatus(BaseModel):
    category_name: str
    spent: float
    budget: float

class DailyTipRequest(BaseModel):
    user_id: int
    current_streak: int
    spending_context: List[CategoryStatus]
    daily_mood_input: Optional[str] = None

class DailyTipResponse(BaseModel):
    tip_title: str
    tip_body: str

# --- 3. Weekly Financial Review ---
class WeeklyReviewRequest(BaseModel):
    user_id: int
    total_spent: float
    total_budget: float
    top_categories: dict

class WeeklyReviewResponse(BaseModel):
    review_paragraph: str
    action_item: str

# --- 4. Personalized Micro-Goals/Suggestions ---
class MicroGoalsRequest(BaseModel):
    user_id: int
    financial_focus: str

class MicroGoal(BaseModel):
    title: str
    description: str
    xp_reward: int

class MicroGoalsResponse(BaseModel):
    goals: List[MicroGoal]
