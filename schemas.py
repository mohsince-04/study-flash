from typing import List
from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    question: str = Field(description="The multiple-choice question text")
    options: List[str] = Field(
        description="A list of 4 distinct choices/options (e.g., ['A) ...', 'B) ...', 'C) ...', 'D) ...'])"
    )
    correct_answer: str = Field(
        description="The exact text or letter of the correct option from the options list"
    )
    explanation: str = Field(
        description="Why this answer is correct and why others are incorrect"
    )
    difficulty: str = Field(description="Difficulty level: Easy, Medium, or Hard")


class QuizReport(BaseModel):
    title: str = Field(
        description="A catchy, relevant title for the quiz based on the source text"
    )
    topic_summary: str = Field(
        description="A brief 2-3 sentence summary of the core concepts covered"
    )
    questions: List[QuizQuestion] = Field(
        description="A list of generated multiple-choice quiz questions"
    )
