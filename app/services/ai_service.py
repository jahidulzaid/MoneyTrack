import os
import json
from openai import AsyncOpenAI
from app.schemas.ai import (
    ChatRequest, DailyTipRequest, DailyTipResponse, 
    WeeklyReviewRequest, WeeklyReviewResponse,
    MicroGoalsRequest, MicroGoalsResponse
)

# Ensure OPENAI_API_KEY is loaded in environment variables (.env)
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL_NAME = "gpt-5.4-mini"


def safe_parse_json(raw_content: str, fallback: dict) -> dict:
    try:
        parsed = json.loads(raw_content)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return fallback

async def generate_chat_reply(request: ChatRequest) -> str:
    system_prompt = (
        "You are Moniv8's AI Money Coach. Be concise, direct, and practical. "
        "Use 2-4 short sentences by default. "
        "Do not start with filler like 'Absolutely', 'Great question', or long introductions. "
        "Do not use markdown headings or long bullet lists unless the user explicitly asks for a detailed plan. "
        "Give one clear next step whenever possible. Tone: supportive and motivational."
    )
    
    if request.user_context:
        system_prompt += f"\nHere is the user's current financial context: {request.user_context}"

    openai_messages = [{"role": "system", "content": system_prompt}]
    
    for msg in request.messages:
        if msg.role in ["user", "assistant"]:
            openai_messages.append({"role": msg.role, "content": msg.content})

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=openai_messages,
        temperature=0.4,
        max_completion_tokens=140,
    )
    return response.choices[0].message.content

async def generate_daily_tip(request: DailyTipRequest) -> DailyTipResponse:
    system_prompt = """
    You are a smart, supportive AI financial coach.

    Your goal is to generate a short, highly actionable and motivational financial tip based on the user's current behavior.

    Instructions:
    - Identify ONE key insight (overspending, under budget, trend, or habit).
    - Give a SPECIFIC, actionable suggestion (not generic advice).
    - If overspending -> suggest a corrective action.
    - If doing well -> reinforce and encourage continuation.
    - If mood indicates stress -> be empathetic and supportive.
    - Keep tone: motivational, concise, human-like (like a coach, not robotic).
    - Avoid vague phrases like "save more" or "spend less".
    - Use numbers when possible (e.g., "$50 over", "twice this week").

    Output format (STRICT JSON):
    {
    "tip_title": "<short catchy title (max 6 words)>",
    "tip_body": "<1-2 sentence actionable tip>"
    }

    Examples:

    Input: Overspending on dining
    Output:
    {
    "tip_title": "Cut Dining Costs",
    "tip_body": "You're $100 over on dining out. Try cooking at home twice this week to get back on track."
    }

    Input: Good spending behavior
    Output:
    {
    "tip_title": "Great Budget Control",
    "tip_body": "Nice work staying under budget! Keep tracking daily to maintain this momentum."
    }
    """

    user_prompt = json.dumps(
        {
            "streak_days": request.current_streak,
            "spending_context": [cat.model_dump() for cat in request.spending_context],
            "daily_mood_input": request.daily_mood_input or None,
        },
        ensure_ascii=True,
    )
    
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"}
    )
    
    fallback = {
        "tip_title": "Stay Consistent",
        "tip_body": "Keep tracking your spending daily. Small consistent actions build strong financial habits."
    }

    data = safe_parse_json(response.choices[0].message.content, fallback)
    return DailyTipResponse(**data)

async def generate_weekly_review(request: WeeklyReviewRequest) -> WeeklyReviewResponse:
    system_prompt = """
    You are a smart, supportive AI financial coach.

    Your goal is to summarize the user's weekly financial performance and provide one practical next-step action.

    Instructions:
    - Analyze spending versus budget and identify the most important weekly pattern.
    - Mention concrete numbers when helpful.
    - Keep the tone motivational and constructive.
    - Avoid blame or shaming language.
    - Keep output concise and mobile-friendly.

    Output format (STRICT JSON):
    {
    "review_paragraph": "<2-3 sentence weekly summary with one key insight>",
    "action_item": "<one specific action for next week>"
    }

    Examples:

    Input: Spending above budget due to dining out
    Output:
    {
    "review_paragraph": "You spent $980 against a $900 budget this week, with dining out driving most of the overage. The strong part is that groceries stayed controlled, which shows your core habits are improving.",
    "action_item": "Set a dining-out cap of 2 meals next week and move the saved amount to debt payment."
    }

    Input: Spending below budget
    Output:
    {
    "review_paragraph": "Great week: you spent $760 on a $900 budget and kept your top categories stable. That consistency is helping build long-term momentum.",
    "action_item": "Auto-transfer $25 to savings right after payday to lock in this week's progress."
    }
    """

    user_prompt = json.dumps(
        {
            "total_spent": request.total_spent,
            "total_budget": request.total_budget,
            "top_categories": request.top_categories,
        },
        ensure_ascii=True,
    )
    
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"}
    )

    fallback = {
        "review_paragraph": "You made progress this week by staying engaged with your finances. Keep tracking your categories to spot trends earlier.",
        "action_item": "Choose one category to reduce by a fixed amount next week and track it daily."
    }

    data = safe_parse_json(response.choices[0].message.content, fallback)
    return WeeklyReviewResponse(**data)

async def generate_micro_goals(request: MicroGoalsRequest) -> MicroGoalsResponse:
    system_prompt = """
    You are a smart, supportive AI financial coach.

    Your goal is to generate exactly 3 practical financial micro-goals for the user's current focus area.

    Instructions:
    - Generate exactly 3 unique goals.
    - Each goal must be specific, actionable, and small enough to complete within a week.
    - Keep language concise and clear for mobile UI.
    - Match goals to the user's focus area.
    - xp_reward must be an integer between 10 and 50.
    - Avoid generic advice like "save more" without a concrete action.

    Output format (STRICT JSON):
    {
    "goals": [
        {
            "title": "<max 6 words>",
            "description": "<1 sentence concrete action>",
            "xp_reward": <integer 10-50>
        }
    ]
    }

    Examples:

    Input focus: debt_payoff
    Output:
    {
    "goals": [
        {"title": "Extra Debt Payment", "description": "Pay an extra $20 toward your highest-interest debt this week.", "xp_reward": 25},
        {"title": "Cancel One Subscription", "description": "Cancel one unused subscription and redirect that amount to debt.", "xp_reward": 30},
        {"title": "No-Spend Day", "description": "Complete one no-spend day and apply the saved cash to debt.", "xp_reward": 20}
    ]
    }
    """

    user_prompt = json.dumps(
        {
            "financial_focus": request.financial_focus,
        },
        ensure_ascii=True,
    )

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"}
    )

    fallback = {
        "goals": [
            {
                "title": "Track Daily Spending",
                "description": "Log every expense for the next 7 days to identify one area to improve.",
                "xp_reward": 20,
            },
            {
                "title": "Set Category Cap",
                "description": "Set a weekly limit for one category and stay within it.",
                "xp_reward": 25,
            },
            {
                "title": "Move Small Amount",
                "description": "Transfer a small fixed amount to savings or debt this week.",
                "xp_reward": 20,
            },
        ]
    }

    data = safe_parse_json(response.choices[0].message.content, fallback)
    return MicroGoalsResponse(**data)
