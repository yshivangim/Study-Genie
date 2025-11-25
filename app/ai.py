import os
import reflex as rx
from openai import OpenAI
import json
import logging
import base64


def get_client():
    """Initialize OpenAI client lazily."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        error_msg = "OPENAI_API_KEY is not set. Please ensure it is defined in your environment variables."
        logging.error(error_msg)
        raise ValueError(error_msg)
    return OpenAI(api_key=api_key)


def parse_json_response(response_text: str | None):
    """Extract and parse JSON from the AI's response."""
    if not response_text:
        logging.error("AI response was empty.")
        return None
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logging.exception(f"Error parsing JSON: {e}\nResponse text: {response_text}")
        if "on" in response_text:
            try:
                json_str = response_text.split("on")[1].split("")[0]
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError) as fix_e:
                logging.exception(f"Failed to fix JSON: {fix_e}")
        return None


PROMPTS = {
    "Notes": {
        "prompt": "Generate comprehensive study notes for the given topic/text. Include 8-12 detailed bullet points covering key concepts.",
        "json_structure": '{"heading": "Topic Heading", "bullets": ["Detailed point 1", "Detailed point 2", ...], "mnemonic": "A helpful memory aid"}',
    },
    "Summary": {
        "prompt": "Summarize the given topic/text.",
        "json_structure": '{"summary": "string", "takeaways": ["string", "string", ...]}',
    },
    "Explain": {
        "prompt": "Explain the given topic/text simply.",
        "json_structure": '{"steps": ["string", ...], "example": "string", "analogy": "string"}',
    },
    "Quiz": {
        "prompt": "Create a 5-question multiple-choice quiz on the given topic/text.",
        "json_structure": '{"questions": [{"question": "string", "options": ["string", ...], "correct_answer": int}]}',
    },
    "Flashcards": {
        "prompt": "Create 8-10 flashcards for the given topic/text.",
        "json_structure": '{"cards": [{"question": "string", "answer": "string"}]}',
    },
}


def generate_content(mode: str, user_input: str):
    """Generic function to call OpenAI API with a structured prompt."""
    if mode not in PROMPTS:
        return None
    prompt_details = PROMPTS[mode]
    system_prompt = f"You are StudyGenie, an AI study assistant. Your goal is to produce clear, concise, and undergraduate-level educational content. Respond ONLY with a valid JSON object matching this structure: {prompt_details['json_structure']}"
    user_prompt = f"{prompt_details['prompt']}\n\n--- TOPIC/TEXT ---\n{user_input}"
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return parse_json_response(content)
    except Exception as e:
        logging.exception(f"An error occurred while calling OpenAI: {e}")
        return None


def generate_content_from_image(mode: str, user_input: str, image_path: str):
    """Function to call OpenAI Vision API."""
    if mode not in PROMPTS:
        return None
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logging.exception(f"Error reading image file: {e}")
        return None
    prompt_details = PROMPTS[mode]
    system_prompt = f"You are StudyGenie, an AI study assistant. Your goal is to produce clear, concise, and undergraduate-level educational content based on the provided image and text. Respond ONLY with a valid JSON object matching this structure: {prompt_details['json_structure']}"
    user_content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
        },
        {
            "type": "text",
            "text": f"{prompt_details['prompt']}\n\n--- USER QUERY ---\n{(user_input if user_input else 'Analyze the image.')}",
        },
    ]
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return parse_json_response(content)
    except Exception as e:
        logging.exception(f"An error occurred while calling OpenAI Vision API: {e}")
        return None