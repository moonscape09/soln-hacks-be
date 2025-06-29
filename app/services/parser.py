import os
import re
import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

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
        "You are a helpful assistant that converts drawing instructions into JSON. "
        "Return a JSON object with only one key: 'shapes', which is a list of objects. "
        "Each shape must include a 'type' (rectangle, circle, ellipse, line, or text) and "
        "appropriate properties:\n"
        "- rectangle: x, y, width, height, color\n"
        "- circle: x, y, radius, color\n"
        "- ellipse: x, y, radiusX, radiusY, color\n"
        "- line: points (array of x,y), stroke, strokeWidth\n"
        "- text: text, x, y, fontSize, color\n"
        "Example:\n"
        "Prompt: Draw a blue rectangle and write Hello\n"
        "Output: {\"shapes\": ["
        "{\"type\": \"rectangle\", \"x\": 100, \"y\": 100, \"width\": 200, \"height\": 100, \"color\": \"blue\"}, "
        "{\"type\": \"text\", \"text\": \"Hello\", \"x\": 150, \"y\": 250, \"fontSize\": 24, \"color\": \"black\"}"
        "]}"
    )

    user_prompt = f"Prompt: {prompt}\nOutput:"
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    logger.debug(f"Calling Gemini LLM with prompt: {user_prompt}")
    try:
        full_prompt = system_prompt + "\n" + user_prompt
        response = model.generate_content([full_prompt])
        content = response.text
        logger.debug(f"Gemini LLM raw response: {content}")
        lines = [line for line in content.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
        parsed = json.loads(cleaned)
        logger.debug(f"Gemini LLM parsed JSON: {parsed}")
        return parsed
    except Exception as e:
        logger.error(f"Gemini LLM call or JSON parsing failed: {e}")
        return {"shapes": []}

def flatten_points(shapes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for shape in shapes:
        if shape.get("type") == "line" and isinstance(shape.get("points"), list):
            # Flatten nested [[x, y], [x2, y2]] → [x, y, x2, y2]
            if all(isinstance(pt, list) and len(pt) == 2 for pt in shape["points"]):
                shape["points"] = [coord for pt in shape["points"] for coord in pt]
    return shapes


def parse_prompt(prompt: str) -> Dict[str, List[Dict[str, Any]]]:
    try:
        logger.debug(f"parse_prompt: Trying Gemini LLM for prompt: {prompt}")
        llm_result = call_gemini_llm(prompt)
        if isinstance(llm_result, dict) and "shapes" in llm_result:
            logger.debug(f"parse_prompt: Using Gemini LLM result: {llm_result}")
            llm_result["shapes"] = flatten_points(llm_result["shapes"])
            return llm_result

    except Exception as e:
        logger.error(f"parse_prompt: Gemini LLM failed: {e}")

    logger.debug(f"parse_prompt: Falling back to rule-based parser for prompt: {prompt}")
    prompt = prompt.lower()
    shapes = []

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
                shapes.append({
                    "type": "text",
                    "text": "Sample Text",
                    "x": 150,
                    "y": 250,
                    "fontSize": 24,
                    "color": "black"
                })

    text_match = re.search(r'write (.+)', prompt)
    if text_match:
        shapes.append({
            "type": "text",
            "text": text_match.group(1),
            "x": 200,
            "y": 350,
            "fontSize": 28,
            "color": "purple"
        })

    shapes = flatten_points(shapes)
    result = {"shapes": shapes}

    logger.debug(f"parse_prompt: Rule-based result: {result}")
    return result
