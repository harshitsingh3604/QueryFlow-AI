from concurrent.futures import ThreadPoolExecutor
import time


class MockAIService:
    """
    Local AI provider used for development and testing.
    """

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
        """
        Generate responses for multiple prompts concurrently.

        Results are returned in the same order as the input prompts.
        Individual AI failures are returned as per-item errors.
        """
        if not prompts:
            return []

        with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
            futures = [
                executor.submit(self.generate_response, prompt)
                for prompt in prompts
            ]

            results = []

            for future in futures:
                try:
                    response = future.result()

                    results.append({
                        "response": response
                    })

                except Exception:
                    results.append({
                        "error": "AI service unavailable"
                    })

            return results


_ai_service = MockAIService()


def generate_response(prompt):
    """
    Generate a response for a single prompt.
    """
    return _ai_service.generate_response(prompt)


def generate_responses_async(prompts):
    """
    Generate responses for multiple prompts concurrently.
    """
    return _ai_service.generate_responses_async(prompts)