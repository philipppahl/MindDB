from typing import List, Literal
from pydantic import BaseModel, Field
from tqdm.asyncio import tqdm_asyncio
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed

import minddb


class QuizOption(BaseModel):
    """Represents a single multiple-choice option in a quiz question."""
    letter: Literal['a', 'b', 'c', 'd'] = Field(
        description="The option letter (a, b, c, or d)"
    )
    text: str = Field(
        description="The text content of this answer option"
    )


class QuizQuestion(BaseModel):
    """Represents a single multiple-choice quiz question with options and
    explanation."""
    question_text: str = Field(
        description="The text of the question being asked"
    )
    options: List[QuizOption] = Field(
        description="The four possible answer options (a, b, c, d)",
        min_items=4,
        max_items=4
    )
    correct_answer: Literal['a', 'b', 'c', 'd'] = Field(
        description="The letter of the correct answer option"
    )
    explanation: str = Field(
        description="Detailed explanation of why the correct answer is right"
    )


class RevisedQuizQuestion(BaseModel):
    """Represents a single revised multiple-choice quiz question and result
    and justification of the review."""
    review_result: Literal['satisfactory', 'needs_improvement'] = Field(
        description="The result of the review (correct, incorrect, or unclear)"
    )
    justification_for_changes: str = Field(
        description="The justification for any changes made to the question"
    )
    revised_quiz_question: QuizQuestion = Field(
        description=("The revised multiple-choice quiz question with options "
                     "and explanation")
    )

    def to_dict(self):
        revised_quiz_question = self.revised_quiz_question
        return {
            "question": revised_quiz_question.question_text,
            "answer_a": revised_quiz_question.options[0].text,
            "answer_b": revised_quiz_question.options[1].text,
            "answer_c": revised_quiz_question.options[2].text,
            "answer_d": revised_quiz_question.options[3].text,
            "correct_answer": revised_quiz_question.correct_answer,
            "explanation": revised_quiz_question.explanation
        }


def prompt():  # noqa: E501
    return """# Review and Refine Individual Quiz Question

## Task Description
Review a single quiz question and refine it to ensure it is high-quality,
accurate, and effective for learning the lecture material.

This quiz question is part of a set designed to test understanding of the
concepts presented in this lecture. Your review should ensure the question
accurately reflects the lecture content and tests relevant knowledge.

## Lecture Context
{{lecture_summary}}

## Input
{{quiz_question}}

## Review Criteria
Evaluate this question on:

1. **Accuracy**: Does the question accurately reflect the content from the lecture?
2. **Clarity**: Is the question clearly worded and unambiguous?
3. **Plausibility of Options**: Are all four options plausible, with no obviously incorrect options?
4. **Distinctiveness**: Are the options clearly distinct from each other?
5. **Explanation Quality**: Is the explanation detailed and educational?
6. **Learning Value**: Does the question test important knowledge from the lecture?
7. **Keyword Highlighting**: Are the most important key terms in the explanation highlighted?

## Output Format
For the reviewed question, follow this exact format:
```
## Review Result [satisfactory, needs_improvement]
## Justification for Changes

## Revised Quiz Question
[QUESTION TEXT]

a) [OPTION a]
b) [OPTION b]
c) [OPTION c]
d) [OPTION d]

**Correct Answer:** [LETTER a, b, c, or d]
**Explanation:** [DETAILED EXPLANATION OF WHY THIS ANSWER IS CORRECT]
```

Please provide your detailed review and refinement for this individual quiz
question.
"""


@retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
async def review_note(note, lecture_summary, semaphore):
    client, model = minddb.async_client()

    async with semaphore:
        coro = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt()
            }],
            max_tokens=1000,
            response_model=RevisedQuizQuestion,
            context={
                'lecture_summary': lecture_summary,
                'quiz_question': note
            }
        )
        note = await asyncio.wait_for(coro, timeout=30)
    return note


async def notes(notes, lecture_summary):
    semaphore = asyncio.Semaphore(1)

    coros = []
    for note in notes:
        coros.append(review_note(note, lecture_summary, semaphore))

    revised_notes = await tqdm_asyncio.gather(*coros)
    return revised_notes
