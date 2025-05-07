# ab_sdk/agent.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# one-time global configuration
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "No GEMINI_API_KEY found. "
        "Please set GEMINI_API_KEY in your environment or in a .env file."
    )
genai.configure(api_key=api_key)


class Agent:
    """
    A wrapper around Google Gemini via the legacy google-generativeai SDK.
    Automatically picks up GEMINI_API_KEY and lets you override the model
    for easier testing.
    """

    def __init__(
        self,
        name: str,
        instructions: str,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        model: genai.GenerativeModel = None,       # ← new param
    ):
        self.name = name
        self.instructions = instructions

        if model is not None:
            # test override
            self.model = model
        else:
            # real model
            self.model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=instructions,
                generation_config=genai.GenerationConfig(temperature=temperature),
            )

    def run(self, prompt: str = "") -> str:
        """
        Sends a single-turn prompt to Gemini and returns the generated text.
        """
        response = self.model.generate_content(prompt)
        return response.text
