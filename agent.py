
"""StudyBuddy AI: assignment prioritization, scheduling, and Gemini advice."""

import os
import json
from datetime import date, datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()


def prioritize_tasks(tasks):
    """Tool 1: rank assignments by urgency, importance, and effort."""
    today = date.today()
    ranked = []

    for task in tasks:
        title = str(task.get("title", "")).strip()
        if not title:
            continue

        try:
            due = datetime.strptime(str(task.get("due", "")), "%Y-%m-%d").date()
            hours = max(0.25, min(24.0, float(task.get("hours", 1))))
            importance = max(1, min(5, int(task.get("importance", 3))))
        except (ValueError, TypeError):
            raise ValueError("Enter a valid due date, hours, and importance (1–5).")

        days_left = (due - today).days
        urgency = (
            10 if days_left < 0 else
            8 if days_left == 0 else
            6 if days_left <= 2 else
            4 if days_left <= 7 else 1
        )

        score = urgency * 3 + importance * 2 + min(hours, 8) * 0.3

        ranked.append({
            "title": title[:120],
            "due": due.isoformat(),
            "hours": hours,
            "importance": importance,
            "days_left": days_left,
            "score": round(score, 1)
        })

    return sorted(ranked, key=lambda x: (-x["score"], x["due"]))


def allocate_study_time(ranked, available_hours):
    """Tool 2: allocate study hours by assignment priority."""
    remaining = float(available_hours)
    schedule = []

    for task in ranked:
        if remaining <= 0:
            break

        allocation = round(min(task["hours"], remaining), 2)

        schedule.append({
            "title": task["title"],
            "hours": allocation,
            "next_step": (
                f"Work on {task['title']} for {allocation:g} hour(s); "
                "start with the first unfinished requirement."
            )
        })

        remaining = round(remaining - allocation, 2)

    return schedule, remaining


def run_study_agent(tasks, available_hours):
    """Use planning tools, then ask Gemini for personalized study advice."""

    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Add at least one assignment.")

    try:
        available_hours = float(available_hours)
    except (TypeError, ValueError):
        raise ValueError("Enter valid available study hours.")

    if not 0.25 <= available_hours <= 24:
        raise ValueError("Study hours must be between 0.25 and 24.")

    ranked = prioritize_tasks(tasks)

    if not ranked:
        raise ValueError("Add at least one assignment with a title.")

    schedule, remaining = allocate_study_time(ranked, available_hours)

    first = ranked[0]
    reason = (
        "overdue" if first["days_left"] < 0 else
        "due today" if first["days_left"] == 0 else
        f"due in {first['days_left']} day(s)"
    )

    result = {
        "priorities": ranked,
        "schedule": schedule,
        "remaining_hours": remaining,
        "message": f"Start with {first['title']} ({reason}).",
        "tools_used": ["prioritize_tasks", "allocate_study_time"],
        "mode": "rule-based fallback"
    }

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            client = genai.Client(api_key=api_key)

            prompt = f"""
            You are StudyBuddy AI, a friendly student study coach.

            Prioritized assignments:
            {json.dumps(ranked)}

            Study schedule:
            {json.dumps(schedule)}

            Explain which assignment to start first and why.
            Give 2-3 practical study tips.
            Keep your response under 120 words.
            """

            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )

            if response.text:
                result["message"] = response.text
                result["mode"] = "Gemini AI-powered study coach"

        except Exception as e:
            print("Gemini API error:", str(e))
            result["mode"] = "rule-based fallback"

    return result
