from abc import ABC, abstractmethod
import os
import json
from typing import Union
from langchain_google_genai import GoogleGenerativeAI
from jsonschema import validate as json_validate, ValidationError as JSONValidationError


class LLMInterface(ABC):
    @abstractmethod
    def query(self, prompt: str) -> dict:
        """Send a prompt to the LLM and return the structured response"""
        pass


class CustomOutputParser:
    def __init__(self, schema: dict):
        self.schema = schema
        self.json_schema = self._to_json_schema(schema)

    def _to_json_schema(self, schema: dict) -> dict:
        json_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        for field_name, field_info in schema.items():
            field_type = field_info.get("type", "string")
            json_schema["properties"][field_name] = {
                "type": field_type,
                "description": field_info.get("description", "")
            }

            if not field_info.get("optional", False):
                json_schema["required"].append(field_name)

        if not json_schema["required"]:
            json_schema.pop("required")

        return json_schema

    def parse(self, raw_response: str) -> dict:
        try:
            # Remove Markdown-style code fencing
            raw = raw_response.strip()
            if raw.startswith("```"):
                lines = raw.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                raw = "\n".join(lines).strip()

            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")

        try:
            json_validate(instance=parsed, schema=self.json_schema)
        except JSONValidationError as e:
            raise ValueError(f"Validation failed: {e.message}")

        for key in self.schema:
            if key not in parsed:
                parsed[key] = None

        return parsed


class GeminiLLM(LLMInterface):
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash-exp", schema: dict = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        self.model = GoogleGenerativeAI(model=model, google_api_key=self.api_key)

        if schema:
            self.schema = schema
            self.parser = CustomOutputParser(schema)
        else:
            self.schema = None
            self.parser = None

    def query(self, prompts: Union[list, str], schema: dict = None) -> dict:
        """Query Gemini API and return a structured response. Supports per-query schema."""

        local_parser = None

        if schema:
            if not isinstance(schema, dict):
                raise ValueError("Schema must be a dictionary.")
            local_parser = CustomOutputParser(schema)
        elif self.parser:
            local_parser = self.parser

        if isinstance(prompts, str):
            prompts = [prompts]

        formatted_prompts = []
        for prompt in prompts:
            if local_parser:
                json_schema = local_parser.json_schema
                format_instructions = (
                    "\nPlease respond in pure JSON format matching this schema:\n"
                    f"{json.dumps(json_schema, indent=2)}"
                )
                full_prompt = f"{prompt.strip()}\n{format_instructions}"
            else:
                full_prompt = prompt
            formatted_prompts.append(full_prompt)

        full_input = "\n".join(formatted_prompts)
        response = self.model.invoke(full_input)

        if not response:
            return {"success": False, "error": "No response from LLM"}

        if local_parser:
            try:
                parsed = local_parser.parse(response)
                return {"success": True, "data": parsed}
            except Exception as e:
                return {"success": False, "error": str(e), "raw": response}

        return {"success": True, "data": response}
