import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional, List, Type
from pydantic import BaseModel, ValidationError

load_dotenv()

class ABAgent:
    def __init__(
        self,
        name: str,
        instructions: str,
        output_type: Optional[Type[BaseModel]] = None,
        handoffs: Optional[List["ABAgent"]] = None,  # recursive type
    ):
        self.name = name
        self.instructions = instructions
        self.output_type = output_type
        self.handoffs = handoffs or []

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")

        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def run(self, input: str):
        # Check if any handoff agent matches the intent
        for agent in self.handoffs:
            if agent.can_handle(input):
                return agent.run(input)

        prompt = f"{self.instructions}\n\nUser: {input}"
        response = self.model.generate_content(prompt)
        text = response.text.strip()

        if self.output_type:
            try:
                return self.output_type.model_validate_json(text)
            except (ValidationError, TypeError, ValueError) as e:
                return text

        return text

    def can_handle(self, input: str) -> bool:
        """Basic keyword routing logic (customize this as needed)."""
        keywords = self.name.lower().split()
        return any(keyword in input.lower() for keyword in keywords)
