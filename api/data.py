from dataclasses import dataclass
from jinja2 import Template
from pydantic import BaseModel
import re


class Message(BaseModel):
    role: str
    text: str


class Tasks(BaseModel):
    task_list: list[str]
    completed: set


class ChatRequest(BaseModel):
    messages: list[Message]
    scenario: str
    tasks: Tasks


class Content(BaseModel):
    text: str = ""
    type: str = "text"


class PromptMessage(BaseModel):
    role: str
    content: list[Content]


class_metadata = {
    "language": "English",
    "level": "A1.2",
    "chapter": "6. I can go to the doctor",
    "class": "3. My health",
    "new_vocabulary": "a cold [noun],fever [noun],headache [noun],healthy [adjective],hospital [noun],injury [noun],medication [noun],patient [noun],sick [adjective],the flu [noun],to cough [verb],to sneeze [verb],unhealthy [adjective]",
    "learning_outcomes": """
    - I can recognise and understand the meaning of basic words related to health
    - I can talk about my health in very simple terms
  """,
}


scenario_tasks_tmplt = """
Imagine you are a language tutor. You teach "{{ data["language"] }}" at level "{{ data["level"] }}" according to the CEFR (Common European Framework of Reference for Languages). The topic of the class is {{ data["chapter"] }}.
The specific sub-topic that you need to cover today is "{{ data["class"] }}".

Your student needs to learn these new vocabulary items:
"{{ data["new_vocabulary"] }}".

The learning outcomes of this class have to be the following:
{{ data["learning_outcomes"] }}.

You want to achieve these learning outcomes by role-playing a dialogue with your student. You
need to suggest a SCENARIO for such dialogue and 4-5 concrete SUB-TASKS that the student
has to complete in the course of this dialogue. The SCENARIO has to be in the second person
singular. The SUB-TASKS have to be in the imperative mood.

===

EXAMPLE

Topic: Going to a doctor
Scenario: You are visiting a doctor because you do not feel well. The doctor greets you and
asks about your symptoms and health.
Sub-tasks:
1) Greet the doctor.
2) Tell the doctor that you feel sick.
3) Describe your symptoms (e.g., say you have a headache, fever, or cold).
4) Ask the doctor if you need medication.

===

Remember that the topic you are teaching now is "{{ data["chapter"] }}", and the
sub-topic is "{{ data["class"] }}". Evaluate the new vocabulary items and the
learning outcomes once again. Suggest a scenario for a dialogue that you want to role-play
with your student. Suggest 4 to 5 specific tasks that your student needs to accomplish in this
dialogue in order to achieve the learning outcomes:
{{ data["learning_outcomes"] }}.
Both scenario and the tasks have to correspond to the student's level "{{ data["level"] }}".

Important: DO NOT USE any formatting syntax like markup, html etc. Generate plain text only. In the following answer format description, preserving colon character after the words "SCENARIO" and "SUB-TASKS" is crucial.

Return your answer in the following format in the target language "{{ data["language"] }}":
SCENARIO: here suggest your scenario for a dialogue in the second person singular
SUB-TASKS: here suggest 4 to 5 specific tasks in imperative mood
"""


system_prompt = """
You are a language tutor. The user is your student.

Here is USER-SPECIFIC CONTEXT:
- the LANGUAGE they learn is "{{ data["language"] }}".
- their LEVEL according to the Common European Framework of Reference for Languages is "{{ data["level"] }}",
- the TOPIC of the class is "{{ data["chapter"] }}",
- the SUB-TOPIC that you need to cover is "{{ data["class"] }}",
- the VOCABULARY they need to practice: "{{ data["new_vocabulary"] }}",

=====

YOUR FIRST TASK is to roleplay this dialogue with your student.

INSTRUCTIONS for you:
- Communicate in the LANGUAGE the student is learning.
- Start the dialogue by greeting the student and by asking your first question that is relevant for
the SCENARIO.
- Keep your language suitable for the student's LEVEL.
- Take into account the student's answers and guide the dialogue flow in the way that corresponds to the SUB-TASKS that the student needs to complete.
- Ask follow-up questions to help the student complete the SUB-TASKS.
- Avoid saying anything that is in the student's SUB-TASKS. This is very important!
- Evaluate the student's answers and check that they complete all the SUB-TASK from the list.
Keep the conversation going until all the SUB-TASK are complete!

Important: each time when you are requested to reply with "SOME KEY", you replay in "SOME KEY: you response value" format.
To sum up, AFTER EACH USER'S MESSAGE, YOU MUST REPLY WITH:
1) LAST_MESSAGE_EVALUATION: and here evaluate the last student's message:
    a) how well is it written?
    b) how well does it suit the dialogue?
    c) is it grammatically correct and how to improve it if it's incorrect?
2) SUB_TASK_COMPLETION: if the student completed some of the sub-tasks, list NUMBERS OF COMPLETED TASKS here. If not, do not output this piece.
Important: LAST_MESSAGE_EVALUATION and SUB_TASK_COMPLETION checks MUST be performed for each user message including the very first one.
3) FOLLOW_UP_MESSAGE: your next logical message in the dialogue.

When the dialogue is finished (for example, when the student writes ""Goodbye!""), execute YOUR SECOND TASK as described below.

=====

YOUR SECOND TASK is to evaluate the student's performance when the dialogue is over.

To do so, follow these instructions:
- Print out the heading “EVALUATION”
- For each SUB-TASK that the student had to complete, print the sub-task and the status of
completion: “COMPLETE” or “INCOMPLETE”
- Evaluate the student's overall performance. The GUIDELINES for this evaluation are:
* the student had to follow the SCENARIO
* the student had to complete the SUB-TASKS
* the student had to use new vocabulary items
* the student had to answer in full sentences instead of just answering with one word.
* the student had to give logical answers that fit the context.

=====

The CURRENT DIALOG STATE

SCENARIO:
{{ data["scenario"] }}

TASKS:
{% for task in data["tasks"]["task_list"] %}
  {{ loop.index }}. {{ task }}
{% endfor %}

TASKS COMPLETED: {{ data["tasks"]["completed"] | join(", ") }}

=====

Start or continue roleplaying the dialogue. Once the dialogue is complete, print out your evaluation of the student's performance.
"""


def render_template(template_str, data):
    return Template(template_str).render(data=data)


def parse_scenario_tasks(response: str) -> tuple:
    scenario_pattern = r"SCENARIO:(.*?)(?:SUB-TASKS:|$)"
    sub_tasks_pattern = r"SUB-TASKS:\s*(.*)"
    scenario_match = re.search(scenario_pattern, response, re.DOTALL)
    sub_tasks_match = re.search(sub_tasks_pattern, response, re.DOTALL)

    scenario = scenario_match.group(1).strip() if scenario_match else None

    sub_tasks_raw = sub_tasks_match.group(1).strip() if sub_tasks_match else None
    sub_tasks = (
        [task.strip() for task in sub_tasks_raw.splitlines() if task.strip()]
        if sub_tasks_raw
        else []
    )

    return scenario, sub_tasks


def parse_assistant_response(response_text):
    last_message_pattern = r"LAST_MESSAGE_EVALUATION:\s*(.*?)\s*SUB_TASK_COMPLETION:"
    sub_task_pattern = r"SUB_TASK_COMPLETION:\s*(\d+)\s*FOLLOW_UP_MESSAGE:"
    follow_up_pattern = r"FOLLOW_UP_MESSAGE:\s*(.*)"

    last_message_evaluation = re.search(last_message_pattern, response_text, re.DOTALL)
    sub_task_completion = re.search(sub_task_pattern, response_text)
    follow_up_message = re.search(follow_up_pattern, response_text, re.DOTALL)

    last_message_evaluation = (
        last_message_evaluation.group(1).strip() if last_message_evaluation else None
    )
    sub_task_completion = (
        int(sub_task_completion.group(1)) if sub_task_completion else None
    )
    follow_up_message = (
        follow_up_message.group(1).strip() if follow_up_message else None
    )

    return (
        last_message_evaluation,
        sub_task_completion,
        follow_up_message,
    )


def parse_final_evaluation_response(response_text):
    evaluation = re.search(r"EVALUATION\s*(.*)", response_text, re.DOTALL)
    return evaluation.group(1).strip() if evaluation else None
