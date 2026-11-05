# StudyBuddy AI — Agentic Systems Project

A Flask-based study planner with two callable planning tools. This **starter prototype is rule-based**, not yet connected to a generative AI model. The next step will be integrating an LLM with tool selection.

## Run locally on macOS (VS Code Terminal)

```bash
cd StudyBuddy_AI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Agent workflow

1. User enters assignments and available study hours.
2. `prioritize_tasks` scores assignments by urgency, importance, and effort.
3. `allocate_study_time` assigns available hours in priority order.
4. The website explains the priorities and displays the plan.

## Deployment (later step)

Render web service: build `pip install -r requirements.txt`, start `gunicorn app:app`.

Do not commit `.env` or any API keys.
