import asyncio
import logging
from typing import List, Literal
from pydantic import BaseModel, Field

import minddb
import minddb.mindnote.summary
import minddb.mindnote.review


logger = logging.getLogger(__name__)


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
    number: int = Field(
        description="The sequential number of this question"
    )
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


class Notes(BaseModel):
    """Collection of quiz questions generated from lecture content."""
    questions: List[QuizQuestion] = Field(
        description=("List of multiple-choice quiz questions based on the "
                     "lecture content"),
        default_factory=list
    )


def prompt():
    return """
# Generate Anki Flashcard Quizzes

## Task Description
Using the key topics and information provided below, generate a comprehensive
set of multiple-choice quiz questions based on the lecture. Each quiz question
should follow the Anki flashcard format.

## Content Coverage
Using ONLY the topics, concepts, and information listed below, create questions
that:
- Cover all major topics provided
- Span different levels of difficulty (recall, comprehension, application)
- Test understanding of key concepts, case studies, methodologies, and
  practical recommendations

## Input Information
{{summary}}

## Question Format
For each question, follow this exact format:

```
## Question [NUMBER]
[QUESTION TEXT]

a) [OPTION a]
b) [OPTION b]
c) [OPTION c]
d) [OPTION d]

**Correct Answer:** [LETTER a, b, c, or d]

**Explanation:** [DETAILED EXPLANATION OF WHY THIS ANSWER IS CORRECT]
```

## Question Design Guidelines
1. Make questions clear and specific
2. Ensure all four options are plausible (no obviously wrong answers)
3. Avoid ambiguous wording or trick questions
4. For each concept listed in the input information, create at least one
   question
5. Include questions about practical applications, not just theory
6. Make wrong options reasonable enough that they test understanding
7. Ensure explanations reinforce the key learning points

## Sample Question (for reference)
```
## Question 1
What is the primary benefit of [CONCEPT X] as discussed in the lecture?

a) [Plausible but incorrect option]
b) [Correct option based on lecture content]
c) [Plausible but incorrect option]
d) [Plausible but incorrect option]

**Correct Answer:** b

**Explanation:** As explained in the lecture, [CONCEPT X] provides
[EXPLANATION BASED ON LECTURE CONTENT]. This is important because
[ADDITIONAL CONTEXT FROM LECTURE].
```

Now, using ONLY the provided input information, please generate a comprehensive
set of quiz questions following these guidelines.

## Lecture
{{transcript}}
    """


async def get_notes(transcript):
    summary = minddb.mindnote.summary.get_summary(transcript)

    client, model = minddb.client()
    notes = client.messages.create(
        model=model,
        max_tokens=32768,
        messages=[{
            "role": "user",
            "content": prompt()
        }],
        response_model=Notes,
        context={
            'transcript': transcript,
            'summary': summary,
        },
        max_retries=2
    )
    # Wait for 1 minute
    logger.info("Waiting for 1 minute...")
    await asyncio.sleep(60)
    logger.info("Continuing...")
    return await minddb.mindnote.review.notes(notes.questions, summary)
