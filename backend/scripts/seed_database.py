from app.database.mongodb import get_prompts_collection


PROMPT_ID = "Education_Prompt"

PROMPT_TEMPLATE = (
    "You are an expert in education domain. "
    "Answer the following: {{userInput}}"
)


def seed_prompt():
    prompts_collection = get_prompts_collection()

    prompts_collection.update_one(
        {"_id": PROMPT_ID},
        {
            "$set": {
                "template": PROMPT_TEMPLATE
            }
        },
        upsert=True
    )

    print(f"Successfully seeded prompt: {PROMPT_ID}")


if __name__ == "__main__":
    seed_prompt()