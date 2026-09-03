from app.database.mongodb import get_prompts_collection


def get_prompt_template(prompt_id="Education_Prompt"):
    """
    Retrieve a prompt template from the MongoDB prompts collection.
    """
    prompt = get_prompts_collection().find_one({"_id": prompt_id})

    if prompt is None:
        raise ValueError(f"Prompt '{prompt_id}' not found")

    template = prompt.get("template")

    if not template:
        raise ValueError(f"Prompt '{prompt_id}' has no template")

    return template


def build_prompt(template, user_input):
    """
    Replace the {{userInput}} placeholder with the user's question.
    """
    if not user_input or not user_input.strip():
        raise ValueError("userInput cannot be empty")

    if "{{userInput}}" not in template:
        raise ValueError("Prompt template must contain {{userInput}}")

    return template.replace("{{userInput}}", user_input.strip())
