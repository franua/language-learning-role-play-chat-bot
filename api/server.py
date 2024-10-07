import os
from dotenv import load_dotenv
import logging
import json
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from data import *


load_dotenv()

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

app = FastAPI()

# Enable CORS
origins = [os.getenv("SITE_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_cli = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# Generate the SCENARIIO and TASKS
@app.post("/scenario-tasks/")
def scenario_tasks():
    try:
        prompt = render_template(template_str=scenario_tasks_tmplt, data=class_metadata)
        logger.info(f"Scenario Prompt: {prompt}")

        response = openai_cli.chat.completions.create(
            model=model,
            messages=[
                PromptMessage(role="user", content=[Content(text=prompt, type="text")])
            ],
        )

        scenario, tasks = parse_scenario_tasks(response.choices[0].message.content)
        logger.info(f"Scenario Tasks: {scenario}\n\n{tasks}")

        return {
            "scenario": scenario,
            "tasks": tasks,
            "completed": [],
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# The main CHAT
@app.post("/chat/")
def chat(request: ChatRequest, attempt: int = 1):
    try:
        logger.info(f"Request: {request}")
        logger.info(f"Attempt Number: {attempt}")

        data = class_metadata.copy()
        data.update({"scenario": request.scenario, "tasks": request.tasks})

        # Build the chat for AI
        messages = [  # system message
            PromptMessage(
                role="system",
                content=[
                    Content(
                        text=render_template(
                            template_str=system_prompt,
                            data=data,
                        ),
                        type="text",
                    )
                ],
            ),
        ] + [  # the chat interactions
            PromptMessage(role=msg.role, content=[Content(text=msg.text, type="text")])
            for msg in request.messages
        ]

        logger.info(
            f"Sending a Prompt: {json.dumps(messages, default=lambda x: x.dict(), indent=4)}"
        )

        # Call the AI
        response = openai_cli.chat.completions.create(
            model=model,
            messages=messages,
        )

        logger.info(f"OpenAI Response: {response}")

        # Parse AI's response
        response_msg = response.choices[0].message
        last_message_evaluation, sub_task_completion, follow_up_message = (
            parse_assistant_response(response_msg.content)
        )

        # Handle an LLM failing to respond with the expected format situation
        if not follow_up_message or not last_message_evaluation:
            # We might have reached the end of the conversation and it's time to return the final evaluation
            if len(request.tasks.task_list) == len(request.tasks.completed):
                logger.info(f"ALL TASKS COMPLETED!")
                final_evaluation = parse_final_evaluation_response(response_msg.content)
                response_body = {
                    "role": "tutor",
                    "lastMessageEvaluation": final_evaluation,
                    "subTaskCompletion": None,
                    "text": None,
                }
                logger.info(f"API Response Body: {response_body}")
                return response_body

            # Re-try or give up
            if attempt < 3:
                return chat(request, attempt + 1)
            else:
                last_message_evaluation, sub_task_completion, follow_up_message = (
                    "",
                    None,
                    "I am so sorry, could you repeat or rephrase your answer?",
                )

        # Build the API response body
        response_body = {
            "role": response_msg.role,
            "lastMessageEvaluation": last_message_evaluation,
            "subTaskCompletion": sub_task_completion,
            "text": follow_up_message,
        }

        logger.info(f"API Response Body: {response_body}")

        return response_body
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"message": "Language Learning Roleplay Chatbot API"}
