import logging
from typing import List
from pydantic import BaseModel, Field

import minddb

logger = logging.getLogger(__name__)


class LectureTopics(BaseModel):
    """Structured representation of key topics extracted from a lecture."""

    lecture_topic: str = Field(
        description="Brief description of the overall lecture topic"
    )

    key_concepts: List[str] = Field(
        description=("List of key concepts, frameworks, and terminology "
                     "covered in the lecture"),
        default_factory=list
    )

    case_studies_examples: List[str] = Field(
        description=("List of case studies or examples mentioned in the "
                     "lecture"),
        default_factory=list
    )

    methodologies_metrics: List[str] = Field(
        description=("List of methodologies, metrics, or evaluation "
                     "techniques discussed in the lecture"),
        default_factory=list
    )

    practical_recommendations: List[str] = Field(
        description=("List of practical recommendations or best practices "
                     "presented in the lecture"),
        default_factory=list
    )


def prompt():
    return """
# Step 1: Extract Key Topics from Lecture

## Task
Analyze the lecture transcript below and extract:
1. The main topic of the lecture
2. A comprehensive list of key concepts, frameworks, and terminology covered
3. Any case studies or examples mentioned
4. Any methodologies, metrics, or evaluation techniques discussed
5. Practical recommendations or best practices presented

## Output Format
Please organize your findings in the following structure:

```
# Lecture Topic
[Brief description of the overall lecture topic]

# Key Concepts
- [Concept 1]
- [Concept 2]
- [Concept 3]
...

# Case Studies/Examples
- [Example 1]
- [Example 2]
...

# Methodologies/Metrics
- [Methodology/Metric 1]
- [Methodology/Metric 2]
...

# Practical Recommendations
- [Recommendation 1]
- [Recommendation 2]
...
```

## Instructions
1. Read the entire lecture transcript carefully
2. Extract information objectively without adding concepts not present in the
   lecture
3. Be comprehensive - don't miss any significant topics
4. Use the exact terminology from the lecture
5. Keep each bullet point concise but informative

Please analyze the following lecture transcript:

{{transcript}}
    """


def get_summary(transcript):
    topics = get_topics(transcript)

    summary = f"### Lecture Topic\n{topics.lecture_topic}\n\n"
    if topics.key_concepts:
        summary += "### Key Concepts\n"
        summary += '- ' + '\n- '.join(topics.key_concepts) + '\n\n'

    if topics.case_studies_examples:
        summary += "### Case Studies/Examples\n"
        summary += '- ' + '\n- '.join(topics.case_studies_examples) + '\n\n'

    if topics.methodologies_metrics:
        summary += "### Methodologies/Metrics\n"
        summary += '- ' + '\n- '.join(topics.methodologies_metrics) + '\n\n'

    if topics.practical_recommendations:
        summary += "### Practical Recommendations\n"
        summary += ('- ' + '\n- '.join(topics.practical_recommendations) +
                    '\n\n')

    return summary


def get_topics(transcript):
    client, model = minddb.client()
    logger.info("Extracting key topics...")
    topics = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": prompt()
        }],
        response_model=LectureTopics,
        context={'transcript': transcript},
        max_retries=2
    )
    return topics
