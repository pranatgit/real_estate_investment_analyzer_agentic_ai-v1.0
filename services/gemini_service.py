"""Gemini service and numeric coercion helper."""

import json
import re
import time
from typing import Any, Dict

from google import genai
from google.genai import types

from config import config

_RETRIABLE = ("503", "UNAVAILABLE", "overloaded", "429", "RESOURCE_EXHAUSTED")


def as_number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return default
    match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
    return float(match.group(0)) if match else default


class GeminiService:
    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, contents: str, gen_config: types.GenerateContentConfig):
        last_error = None
        for attempt in range(4):
            try:
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=gen_config,
                )
            except Exception as exc:
                last_error = exc
                if attempt == 3 or not any(token in str(exc) for token in _RETRIABLE):
                    raise
                time.sleep(1.5 * (attempt + 1))
        raise last_error

    def analyze_with_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        structured_prompt = (
            f"{prompt}\n\nReturn a JSON object matching this shape:\n"
            f"{json.dumps(output_schema, indent=2)}"
        )
        response = self.generate(
            structured_prompt,
            types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=2048,
                response_mime_type="application/json",
            ),
        )
        text = (response.text or "").strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise
            parsed = json.loads(match.group(0))
        if not isinstance(parsed, dict):
            raise ValueError("Gemini structured output was not a JSON object")
        return parsed


def get_gemini_service(model_name: str = "") -> GeminiService:
    return GeminiService(config.gemini_api_key, model_name or config.gemini_model)
