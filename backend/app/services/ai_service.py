import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiAIService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.7-flash"

    def generate_response(self, prompt):
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return response.text.strip()


class MockAIService:

    def generate_response(self, prompt):
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        delays = {
            "A": 3,
            "B": 1,
            "C": 2,
            "D": 0.5,
        }

        question = prompt.strip()

        delay = delays.get(question, 0)
        time.sleep(delay)

        return f"Response for {question}"

    def generate_responses_async(self, prompts):
        if not prompts:
            return []

        results = [None] * len(prompts)

        def process(index, prompt):
            try:
                return index, {
                    "response": self.generate_response(prompt)
                }
            except Exception:
                return index, {
                    "error": "AI service unavailable"
                }

        with ThreadPoolExecutor(
            max_workers=len(prompts)
        ) as executor:

            futures = [
                executor.submit(
                    process,
                    index,
                    prompt
                )
                for index, prompt in enumerate(prompts)
            ]

            for future in as_completed(futures):
                index, result = future.result()
                results[index] = result

        return results


ai_service = GeminiAIService()


def generate_response(prompt):
    return ai_service.generate_response(prompt)


def generate_responses_async(prompts):
    return ai_service.generate_responses_async(prompts)