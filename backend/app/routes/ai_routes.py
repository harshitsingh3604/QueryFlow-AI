from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError

from app.services.ai_service import (
    generate_response,
    generate_responses_async,
)
from app.services.history_service import save_history
from app.services.prompt_service import (
    build_prompt,
    get_prompt_template,
)


ai_bp = Blueprint("ai", __name__)

MAX_BATCH_SIZE = 10


@ai_bp.post("/ask")
def ask():
    try:
        # ---------------------------------------------------------
        # 1. Validate request body
        # ---------------------------------------------------------
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        user_input = data.get("userInput")

        if not isinstance(user_input, str) or not user_input.strip():
            return jsonify({
                "error": (
                    "userInput is required and must be "
                    "a non-empty string"
                )
            }), 400

        # ---------------------------------------------------------
        # 2. Get prompt template from MongoDB
        # ---------------------------------------------------------
        try:
            template = get_prompt_template("Education_Prompt")
        except ValueError as exc:
            return jsonify({
                "error": str(exc)
            }), 404

        # ---------------------------------------------------------
        # 3. Build final prompt
        # ---------------------------------------------------------
        final_prompt = build_prompt(
            template,
            user_input
        )

        # ---------------------------------------------------------
        # 4. Generate AI response
        # ---------------------------------------------------------
        try:
            response = generate_response(final_prompt)
        except Exception as exc:
            print("AI ERROR:", repr(exc))

            return jsonify({
                "error": "AI service is unavailable"
            }), 502

        # ---------------------------------------------------------
        # 5. Save request/response history
        # ---------------------------------------------------------
        try:
            save_history(
                user_input=user_input.strip(),
                prompt=final_prompt,
                response=response,
                prompt_id="Education_Prompt",
            )
        except PyMongoError:
            return jsonify({
                "error": "Failed to save request history"
            }), 500

        # ---------------------------------------------------------
        # 6. Return response
        # ---------------------------------------------------------
        return jsonify({
            "response": response
        }), 200

    except PyMongoError:
        return jsonify({
            "error": "Database service is unavailable"
        }), 500

    except RuntimeError:
        return jsonify({
            "error": "AI service is unavailable"
        }), 500

    except ValueError:
        return jsonify({
            "error": "Invalid input provided"
        }), 400

    except Exception:
        return jsonify({
            "error": "Internal server error"
        }), 500


@ai_bp.post("/ask/batch")
def ask_batch():
    try:
        # ---------------------------------------------------------
        # 1. Validate request body
        # ---------------------------------------------------------
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        user_inputs = data.get("userInputs")

        if not isinstance(user_inputs, list):
            return jsonify({
                "error": "userInputs is required and must be an array"
            }), 400

        if not user_inputs:
            return jsonify({
                "error": "userInputs cannot be empty"
            }), 400

        if len(user_inputs) > MAX_BATCH_SIZE:
            return jsonify({
                "error": f"Maximum batch size is {MAX_BATCH_SIZE}"
            }), 400

        # Every item must be a non-empty string.
        for user_input in user_inputs:
            if not isinstance(user_input, str) or not user_input.strip():
                return jsonify({
                    "error": (
                        "Every userInputs item must be "
                        "a non-empty string"
                    )
                }), 400

        # ---------------------------------------------------------
        # 2. Get prompt template from MongoDB
        # ---------------------------------------------------------
        #
        # IMPORTANT:
        # Prompt errors are handled separately from AI errors.
        #
        try:
            template = get_prompt_template("Education_Prompt")
        except ValueError as exc:
            return jsonify({
                "error": str(exc)
            }), 404

        # ---------------------------------------------------------
        # 3. Build final prompt for every input
        # ---------------------------------------------------------
        prompts = []

        for user_input in user_inputs:
            final_prompt = build_prompt(
                template,
                user_input
            )
            prompts.append(final_prompt)

        # ---------------------------------------------------------
        # 4. Generate AI responses concurrently
        # ---------------------------------------------------------
        try:
            responses = generate_responses_async(prompts)

        except Exception as exc:
            # Log the actual exception on the server,
            # but never expose it to the client.
            print("GEMINI BATCH ERROR:", repr(exc))

            return jsonify({
                "error": "AI service is unavailable"
            }), 502

        # ---------------------------------------------------------
        # 5. Save every result to history
        # ---------------------------------------------------------
        batch_results = []

        for user_input, prompt, result in zip(
            user_inputs,
            prompts,
            responses
        ):
            item = {
                "userInput": user_input.strip()
            }

            try:
                # Successful AI response
                if "response" in result:
                    response = result["response"]

                    save_history(
                        user_input=user_input.strip(),
                        prompt=prompt,
                        response=response,
                        prompt_id="Education_Prompt",
                    )

                    item["response"] = response

                # Individual AI failure
                else:
                    error = result.get(
                        "error",
                        "AI service unavailable"
                    )

                    save_history(
                        user_input=user_input.strip(),
                        prompt=prompt,
                        response=None,
                        prompt_id="Education_Prompt",
                        error=error,
                    )

                    item["error"] = error

            except PyMongoError:
                return jsonify({
                    "error": "Failed to save request history"
                }), 500

            batch_results.append(item)

        # ---------------------------------------------------------
        # 6. Return results in original input order
        # ---------------------------------------------------------
        return jsonify({
            "responses": batch_results
        }), 200

    except PyMongoError:
        return jsonify({
            "error": "Database service is unavailable"
        }), 500

    except RuntimeError:
        return jsonify({
            "error": "AI service is unavailable"
        }), 500

    except ValueError:
        return jsonify({
            "error": "Invalid input provided"
        }), 400

    except Exception:
        return jsonify({
            "error": "Internal server error"
        }), 500