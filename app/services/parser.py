import os
import re
import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SHAPE_KEYWORDS = {
    "rectangle": "rectangle",
    "rect": "rectangle",
    "circle": "circle",
    "ellipse": "ellipse",
    "square": "rectangle",
    "text": "text",
    "line": "line"
}

def call_gemini_llm(prompt: str) -> Dict[str, List[Dict[str, Any]]]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set.")
        raise RuntimeError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    system_prompt = (
        "You are a helpful assistant that converts drawing instructions into JSON for Konva JS. You should be familiar with the documentation for the shapes. "
        "Given a user's prompt, return a JSON object with two keys: 'shapes' (a list of shapes to draw) "
        "and 'texts' (a list of text annotations). Each shape should have a type (rectangle, circle, ellipse), "
        "coordinates, size, and color. Each text should have the text, coordinates, fontSize, and color. For the lines follow this" \
        "Output: {\"shapes\": [{\"type\": \"rectangle\", \"x\": 100, \"y\": 100, \"width\": 200, \"height\": 100, \"color\": \"blue\"}], \"texts\": [{\"text\": \"Hello\", \"x\": 150, \"y\": 250, \"fontSize\": 24, \"color\": \"black\"}]}\n"
        "Always return valid JSON."
    )

    user_prompt = f"Prompt: {prompt}\nOutput:"
    # Use the cheapest available Gemini model for text generation
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    logger.debug(f"Calling Gemini LLM with prompt: {user_prompt}")
    try:
        # Combine system instructions and user prompt as a single user message
        full_prompt = system_prompt + "\n" + user_prompt
        response = model.generate_content([full_prompt])
        content = response.text
        logger.debug(f"Gemini LLM raw response: {content}")
        # Remove code block markers if present (robust)
        lines = [line for line in content.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
        parsed = json.loads(cleaned)
        logger.debug(f"Gemini LLM parsed JSON: {parsed}")
        return parsed
    except Exception as e:
        logger.error(f"Gemini LLM call or JSON parsing failed: {e}")
        return {"shapes": [], "texts": [], "lines": []}

def parse_prompt(prompt: str) -> Dict[str, List[Dict[str, Any]]]:
    # Try Gemini LLM first
    try:
        logger.debug(f"parse_prompt: Trying Gemini LLM for prompt: {prompt}")
        llm_result = call_gemini_llm(prompt)
        if llm_result.get("shapes") or llm_result.get("texts"):
            logger.debug(f"parse_prompt: Using Gemini LLM result: {llm_result}")
            return llm_result
    except Exception as e:
        logger.error(f"parse_prompt: Gemini LLM failed: {e}")

    # Fallback to rule-based
    logger.debug(f"parse_prompt: Falling back to rule-based parser for prompt: {prompt}")
    prompt = prompt.lower()
    shapes = []
    texts = []
    lines = []
    for keyword, shape_type in SHAPE_KEYWORDS.items():
        if keyword in prompt:
            if shape_type == "rectangle":
                shapes.append({
                    "type": "rectangle",
                    "x": 100 + 120 * len(shapes),
                    "y": 100,
                    "width": 100,
                    "height": 60,
                    "color": "blue"
                })
            elif shape_type == "circle":
                shapes.append({
                    "type": "circle",
                    "x": 300 + 120 * len(shapes),
                    "y": 200,
                    "radius": 50,
                    "color": "red"
                })
            elif shape_type == "ellipse":
                shapes.append({
                    "type": "ellipse",
                    "x": 200 + 120 * len(shapes),
                    "y": 300,
                    "radiusX": 60,
                    "radiusY": 30,
                    "color": "green"
                })
            elif shape_type == "text":
                texts.append({
                    "text": "Sample Text",
                    "x": 150,
                    "y": 250,
                    "fontSize": 24,
                    "color": "black"
                })

    text_match = re.search(r'write (.+)', prompt)
    if text_match:
        texts.append({
            "text": text_match.group(1),
            "x": 200,
            "y": 350,
            "fontSize": 28,
            "color": "purple"
        })

    result = {"shapes": shapes, "texts": texts}
    logger.debug(f"parse_prompt: Rule-based result: {result}")
    return result 