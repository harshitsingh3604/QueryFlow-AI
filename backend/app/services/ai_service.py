import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv # type: ignore
from google import genai

load_dotenv()


class GeminiAIService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(api_key=api_key)

        # Current stable Flash model
        self.model = "gemini-3.6-flash"

    def generate_response(self, prompt, max_retries=3):

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        for attempt in range(max_retries):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response"
                    )

                return response.text.strip()

            except Exception as exc:

                error_message = str(exc)

                is_temporary_error = (
                    "503" in error_message
                    or "UNAVAILABLE" in error_message
                )

                if is_temporary_error and attempt < max_retries - 1:

                    delay = 2 ** attempt

                    print(
                        f"Gemini 503 error. "
                        f"Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)

                    continue

                raise

        raise RuntimeError(
            "Gemini service unavailable after retries"
        )

    def generate_responses_async(self, prompts):

        if not prompts:
            return []

        results = [None] * len(prompts)

        def process(index, prompt):

            try:

                response = self.generate_response(prompt)

                return index, {
                    "response": response
                }

            except Exception as exc:

                print(
                    f"Gemini error for item {index}:",
                    repr(exc)
                )

                return index, {
                    "error": "AI service unavailable"
                }

        # Maximum 3 Gemini requests at the same time
        max_workers = min(3, len(prompts))

        with ThreadPoolExecutor(
            max_workers=max_workers
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
            max_workers=min(3, len(prompts))
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