# Diet Driven Health — Design Document

**Date:** 2026-03-09
**Status:** Approved

## Problem Statement

Provide personalized diet recommendations for people taking a holistic approach to health, with a focus on autoimmune conditions (Lupus) and renal involvement. The app generates weekly meal plans with recipes tailored to the user's skill level, health goals, and dietary restrictions, tracks adherence, and manages grocery lists with cost awareness.

## Target User

Single user (the developer), intermediate cooking skill level, managing Lupus with potential renal involvement. Designed for personal use with potential to expand later.

## Architecture

- **Backend:** Python FastAPI with SQLAlchemy ORM and SQLite
- **Frontend:** React with TypeScript and Tailwind CSS (responsive for phone + laptop)
- **Auth:** Simple username/password login
- **AI Strategy:** Database-first with rule-based recommendations. Claude Code skills used for offline analysis. AI-powered generation (via API) planned for later.

## Core Data Model

### User Profile
- Cooking skill level (beginner/intermediate/advanced)
- Health conditions and goals
- Configurable dietary restrictions and preferences (low-sodium, anti-inflammatory, low-potassium, gluten-free, etc.)

### Recipe
- Name, description, ingredients (with quantities and units), instructions (steps)
- Prep time, cook time, total time, difficulty level, servings
- Tags: anti-inflammatory, kidney-friendly, low-sodium, etc.
- Autoimmune health score (1-5)
- Nutritional info: calories, protein, sodium, potassium, phosphorus (key for renal health)
- Source: "seeded" or "personal" (user-uploaded)

### Meal Plan
- Weekly plan: 7 days x 3 meals (breakfast, lunch, dinner)
- Generated based on user profile constraints
- Links to specific recipes, supports swapping individual meals
- Historical: past meal plans are preserved

### Dish Log
- Date cooked, recipe reference
- User rating (1-5), free-text notes
- "Would make again" flag
- Tracks adherence to the meal plan

### Grocery List
- Auto-generated from a meal plan's ingredients
- Consolidated (no duplicate items), grouped by store section (produce, dairy, meat, etc.)
- Rough cost estimate per item and total
- Check-off items as you shop

## Features

### User Profile Setup
- Onboarding flow: set cooking skill, health conditions, dietary restrictions
- Editable profile page

### Meal Plan Generator
- Select a week, generate a 7-day meal plan
- Rule-based engine: filters by dietary restrictions, skill level, health tags
- Balances variety: no repeated dishes, mix of cuisines, spread of prep times
- Swap individual meals if a suggestion doesn't work
- View current and past meal plans

### Recipe Browser
- Browse/search by tags, difficulty, time, health score
- Detailed recipe view with ingredients, steps, nutritional breakdown
- Add personal notes and ratings after cooking

### Recipe Upload & Import
- Paste unstructured recipe text (from websites, cookbooks, personal notes)
- Basic parsing to extract name, ingredients, and steps
- User reviews and corrects parsed result before saving
- Tagged as "personal" and factored into preference analysis

### Dish History & Ratings
- Log when you cooked a dish, rate it, note what you'd change
- Filter by rating, date, healthiness score
- Favorites list for quick access to top-rated dishes

### Grocery List
- Auto-generated from the active meal plan
- Ingredients consolidated and grouped by store section
- Rough cost estimate per item and total (store-specific pricing planned for later)
- Check-off items as you shop (mobile-friendly)

### Dashboard
- Weekly meal plan at a glance
- Adherence tracking: did you cook the planned meals?
- Quick stats: meals cooked this week, average health score, budget spent

## Claude Code Skills Architecture

Skills live in `.claude/skills/` and are triggered manually by the developer during Claude Code sessions. They read from the app's SQLite database and write enriched data back.

### Planned Skills

1. **Recipe Analyzer** — Processes uploaded recipes to extract flavor profiles, ingredient patterns, cuisine preferences, cooking style tendencies
2. **User Profile Builder** — Synthesizes ratings, dish history, uploads, and adherence data into expanding user memory files that capture evolving preferences
3. **Meal Plan Optimizer** — Uses enriched user profile to improve the recommendation engine's rules and weights

### Data Flow

```
User uploads recipe (free text)
  -> App parses into structured format
  -> User reviews/corrects -> saved to DB

User rates dishes, follows/swaps meal plans
  -> Activity logged to DB

Developer runs Claude Code skills periodically
  -> Skills read DB exports
  -> Analyze patterns, build user memory files
  -> Memory files committed to repo
  -> App loads memory files to improve recommendations
```

## Project Structure

```
diet_driven_health/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic (recommender, parser)
│   │   └── data/         # Seed recipes, user memory files
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Route-level views
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript types
│   └── package.json
├── .claude/
│   └── skills/           # Claude Code skills for analysis
├── docs/
│   └── plans/            # Design & implementation docs
└── data/
    └── seed_recipes/     # Initial recipe dataset
```

## Future Enhancements (Not in Scope for V1)

- AI-powered meal plan generation via Claude API
- Store-specific grocery pricing (Kroger/Walmart API)
- Photo-based recipe upload (OCR)
- Multiple user support
- Mobile native app (PWA)
