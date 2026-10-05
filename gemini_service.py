import json
import os

import streamlit as st
from google import genai


def get_api_key():
    """Get Gemini API key from Streamlit Secrets or environment."""

    try:
        key = st.secrets.get("GEMINI_API_KEY", "")

        if key:
            return key

    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "")


class GeminiService:

    def __init__(self):

        api_key = get_api_key()

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to Streamlit Secrets."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        # Current model for new Gemini API users
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

    def generate(
        self,
        prompt,
        use_search=False
    ):
        """Generate normal text using Gemini Interactions API."""

        kwargs = {
            "model": self.model,
            "input": prompt,
        }

        if use_search:
            kwargs["tools"] = [
                {
                    "type": "google_search"
                }
            ]

        interaction = self.client.interactions.create(
            **kwargs
        )

        return interaction.output_text

    def generate_json(
        self,
        prompt,
        use_search=False
    ):
        """
        Ask Gemini to return JSON.

        We intentionally parse the response ourselves so
        the same method works with the Interactions API.
        """

        search_instruction = ""

        if use_search:

            search_instruction = """
Use Google Search to research current information.

Prioritize:

1. Official government websites
2. Official university websites
3. Official organization websites
4. Reliable secondary sources

Do not invent requirements or URLs.
"""

        full_prompt = f"""
You are an expert AI case manager.

{search_instruction}

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add explanations before or after the JSON.

{prompt}
"""

        kwargs = {
            "model": self.model,
            "input": full_prompt,
        }

        if use_search:

            kwargs["tools"] = [
                {
                    "type": "google_search"
                }
            ]

        interaction = self.client.interactions.create(
            **kwargs
        )

        text = interaction.output_text.strip()

        # Remove accidental markdown fences
        if text.startswith("```json"):
            text = text[7:]

        if text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:

            return json.loads(text)

        except json.JSONDecodeError as e:

            raise RuntimeError(
                "Gemini returned invalid JSON.\n\n"
                f"Gemini response:\n{text}\n\n"
                f"JSON error: {e}"
            )
