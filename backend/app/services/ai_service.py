class MockAIService:
    """
    Local AI provider used for development and testing.
    """

    def generate_response(self, prompt):
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        return (
            "[Mock AI Response] "
            f"I received the prompt: {prompt.strip()}"
        )


_ai_service = MockAIService()


def generate_response(prompt):
    """
    Generate a response through the configured AI service.
    """
    return _ai_service.generate_response(prompt)