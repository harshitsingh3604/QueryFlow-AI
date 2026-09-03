from datetime import datetime, timezone

from app.database.mongodb import get_history_collection


def save_history(user_input, prompt, response, prompt_id="Education_Prompt"):
    document = {
        "promptId": prompt_id,
        "userInput": user_input,
        "prompt": prompt,
        "response": response,
        "createdAt": datetime.now(timezone.utc),
    }

    get_history_collection().insert_one(document)
    return document