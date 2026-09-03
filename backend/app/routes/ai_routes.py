from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError

from app.services.ai_service import generate_response
from app.services.history_service import save_history
from app.services.prompt_service import build_prompt, get_prompt_template


ai_bp = Blueprint("ai", __name__)


@ai_bp.post("/ask")
def ask():
    try:
        # 1. Validate request body
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        user_input = data.get("userInput")

        if not isinstance(user_input, str) or not user_input.strip():
            return jsonify({
                "error": "userInput is required and must be a non-empty string"
            }), 400

        # 2. Get prompt template from MongoDB
        try:
            template = get_prompt_template("Education_Prompt")
        except ValueError as exc:
            return jsonify({
                "error": str(exc)
            }), 404

        # 3. Build final prompt
        final_prompt = build_prompt(
            template,
            user_input
        )

        # 4. Generate AI response
        try:
            response = generate_response(final_prompt)
        except Exception:
            return jsonify({
                "error": "AI service is unavailable"
            }), 502

        # 5. Save successful request to history
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

        # 6. Return response
        return jsonify({
            "response": response
        }), 200

    except PyMongoError:
        return jsonify({
            "error": "Database service is unavailable"
        }), 500

    except RuntimeError as exc:
        return jsonify({
            "error": str(exc)
        }), 500

    except Exception:
        return jsonify({
            "error": "Internal server error"
        }), 500