"""Static configuration for the Streamlit UI: model choices and demo databases."""

from __future__ import annotations

from typing import TypedDict


class DemoDatabase(TypedDict):
    """One demo database entry: where it lives and how to talk about it."""

    path: str
    description: str
    questions: list[str]
    # A short label per question, in the same order, for the sample-question pills; the
    # full question is what is asked.
    labels: list[str]


# The sidebar's database sources, shared by `ui.sidebar` and `ui.uploads`.
SOURCE_DEMO = "Demo database"
SOURCE_PATH = "SQLite file path"
SOURCE_UPLOAD_DB = "Upload a SQLite file"
SOURCE_UPLOAD_CSV = "Upload CSV files"
SOURCE_DSN = "Connection string"
SOURCES = [SOURCE_DEMO, SOURCE_PATH, SOURCE_UPLOAD_DB, SOURCE_UPLOAD_CSV, SOURCE_DSN]

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "Custom",
]

OLLAMA_MODELS = [
    "gemma3",
    "qwen3.5:9b-q4_K_M",
    "llama3.1",
    "llama3",
    "mistral",
    "qwen2.5",
    "Custom",
]

DEMO_DATABASES: dict[str, DemoDatabase] = {
    "University": {
        "path": "data/university_agent.db",
        "description": "Students, courses, grades, majors",
        "questions": [
            "How many students are enrolled in each major?",
            "What is the average score for each course?",
            "Which students have the highest average score?",
        ],
        "labels": ["Students per major", "Average score by course", "Top students"],
    },
    "Retail Analytics": {
        "path": "data/retail_analytics.db",
        "description": "Customers, orders, products, returns, stores",
        "questions": [
            "Show total completed sales revenue by customer region.",
            "Which return reasons occur most often?",
            "Which product categories generate the most revenue?",
        ],
        "labels": ["Revenue by region", "Top return reasons", "Revenue by category"],
    },
    "Healthcare Analytics": {
        "path": "data/healthcare_analytics.db",
        "description": "Patients, doctors, hospitals, appointments, treatments",
        "questions": [
            "How many appointments are there for each status?",
            "What is the average treatment cost by hospital city?",
            "Which specialties have the most completed appointments?",
        ],
        "labels": ["Appointments by status", "Treatment cost by city", "Busiest specialties"],
    },
}
