from textassert.schema.project import Criterion, Project, Settings, CriterionResponse
from textwrap import dedent
from typing import Any
import json
import re
from openai import AsyncOpenAI
import instructor

MODEL = "google/gemini-2.5-pro-preview-03-25"


def output_processor(resp: str) -> str:
    """Extract content between the first and last code blocks using regex."""
    match = re.search(r"```.*?\n(.*?)```", resp, re.DOTALL)
    return (
        match.group(1).strip().replace("null", "")
        if match
        else resp.replace("null", "")
    )


def generate_single_criterion_system_prompt(criterion: Criterion) -> str:
    return dedent(f"""
    Your job is it to evaluate a text in regards to a specific aspect. The aspect is: "{criterion.name}" and is described as follows: "{criterion.description}".
    When you find issues with the text (and only if there are issues in regards to your aspect) please quote the sentence and then give a short explanation of why it is an issue.
    At the end please provide a final judgement of whether the text, as a whole, passes the criterion or not.
    You might see feedback from previous iterations of the text. If so check whether the points raised are still valid.
    Reevaluate the entire text as there might have been new sections added.
    Be concise in your explanations.
    If you find no issues, just return an empty list.

    Example text:
    This text is missspelled.
    And this sentence is missing punctuation at the end

    Example response (when judging grammar and spelling):
    ```json
    {{
        "feedbacks": [
            {{
                "quote": "This text is missspelled.",
                "feedback": "Missspelled has an extra 's'"
            }},
            {{
                "quote": "And this sentence is missing punctuation at the end",
                "feedback": "Missing punctuation at the end of the sentence"
            }},
        ],
        "passed": false
    }}
    ```

    Example response (when judging clarity):
    ```json
    {{
        "feedbacks": [],
        "passed": true
    }}
    ```

    Again, evaluate the text in regards to the following aspect: {criterion.name}
    This aspect is described as follows: {criterion.description}
    """)


def generate_previous_feedbacks(criterion: Criterion, project: Project) -> str | None:
    feedback = next(
        (c for c in project.criteria if c.name == criterion.name),
        Criterion(name="", description="", passed=False, feedbacks=[]),
    ).feedbacks
    if len(feedback) == 0:
        return None
    return dedent(f"""
    Feedback from previous iteration:
    ```json
    {json.dumps([f.model_dump() for f in feedback], indent=4)}
    ```
    """)


def generate_single_criterion_user_prompt(
    criterion: Criterion, project: Project
) -> str:
    with open(project.file, "r") as f:
        return f.read()


async def send_request(
    criterion: Criterion, project: Project, settings: Settings
) -> dict[str, Any]:
    client = instructor.from_openai(AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=settings.openrouter_api_key), mode=instructor.Mode.JSON)
    messages = [
        {
            "role": "system",
            "content": generate_single_criterion_system_prompt(criterion),
        },
        {
            "role": "user",
            "content": generate_single_criterion_user_prompt(criterion, project),
        },
    ]
    previous_feedbacks = generate_previous_feedbacks(criterion, project)
    if previous_feedbacks:
        messages.insert(
            1,
            {
                "role": "assistant",
                "content": previous_feedbacks,
            },
        )

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages, # type: ignore
        response_model=CriterionResponse,
        extra_body={"provider":{"require_parameters":True}, "temperature": 0.2}
    )
    if isinstance(response, CriterionResponse):
        return {
            "response": response,
            "criterion": criterion.name,
        }
    else:
        raise ValueError("Invalid response from AI")
