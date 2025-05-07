from abc import ABC, abstractmethod
import os
import json
from typing import Union, Dict, Any, List, Type
from langchain_google_genai import GoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, create_model, ValidationError


class LLMInterface(ABC):
    @abstractmethod
    def query(self, prompt: str) -> dict:
        """Send a prompt to the LLM and return the structured response"""
        pass


class GeminiLLM(LLMInterface):
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash-exp", schema: Dict = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        self.model = GoogleGenerativeAI(model=model, google_api_key=self.api_key)

        if schema:
            self.pydantic_model = self._build_pydantic_model(schema)
            self.parser = PydanticOutputParser(pydantic_object=self.pydantic_model)
        else:
            self.pydantic_model = None
            self.parser = None

    def _build_pydantic_model(self, schema: Dict, model_name="DynamicModel") -> Type[BaseModel]:
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
        else:
            properties = schema  # assume it's already a properties dict

        fields = {}

        for field, config in properties.items():
            if not isinstance(config, dict):
                raise TypeError(f"Invalid config for field '{field}': expected dict, got {type(config).__name__}")

            field_type_str = config.get("type", "string")
            optional = config.get("optional", False)

            if field_type_str == "string":
                field_type = str
            elif field_type_str == "integer":
                field_type = int
            elif field_type_str == "number":
                field_type = float
            elif field_type_str == "boolean":
                field_type = bool
            elif field_type_str == "array":
                item_schema = config.get("items", {"type": "string"})
                item_model = self._build_pydantic_model({"item": item_schema}, model_name + "_" + field)
                item_type = item_model.__annotations__.get("item", Any)
                field_type = List[item_type]
            elif field_type_str == "object":
                nested_schema = {"type": "object", "properties": config.get("properties", {})}
                field_type = self._build_pydantic_model(nested_schema, model_name + "_" + field)
            else:
                field_type = str  # fallback

            default = None if optional else ...
            description = config.get("description", "")
            fields[field] = (field_type, Field(default, description=description))

        return create_model(model_name, **fields)

    def query(self, prompts: Union[str, List[Union[str, tuple]]], schema: Dict = None) -> dict:
        parser = None
        if schema:
            model = self._build_pydantic_model(schema)
            parser = PydanticOutputParser(pydantic_object=model)
        elif self.parser:
            parser = self.parser

        if isinstance(prompts, str):
            prompts = [prompts]

        format_instructions = parser.get_format_instructions() if parser else ""
        formatted_prompts = []

        for prompt in prompts:
            if isinstance(prompt, tuple):
                role, content = prompt
                prompt = f"{role}: {content}"
            elif not isinstance(prompt, str):
                raise ValueError(f"Each prompt must be a string or (role, content) tuple, got: {type(prompt)}")

            full_prompt = f"{prompt.strip()}\n{format_instructions}" if parser else prompt.strip()
            formatted_prompts.append(full_prompt)

        full_input = "\n".join(formatted_prompts)
        response = self.model.invoke(full_input)
        print(response)
        if not response:
            return {"success": False, "error": "No response from LLM"}

        if parser:
            try:
                parsed = parser.parse(response)
                return {"success": True, "data": parsed.dict()}
            except ValidationError as e:
                return {"success": False, "error": str(e), "raw": response}

        return {"success": True, "data": response}
