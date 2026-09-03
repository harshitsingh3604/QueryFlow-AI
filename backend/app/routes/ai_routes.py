from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError

from app.services.ai_service import generate_response
from app.services.history_service import save_history
from app.services.prompt_service import build_prompt, get_prompt_template


ai_bp = Blueprint("ai", __name__)


@ai_bp.post("/ask")
def ask():
    try:
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

        template = get_prompt_template("Education_Prompt")

        final_prompt = build_prompt(
            template,
            user_input
        )

        response = generate_response(final_prompt)

        save_history(
            user_input=user_input.strip(),
            prompt=final_prompt,
            response=response,
            prompt_id="Education_Prompt",
        )

        return jsonify({
            "response": response
        }), 200

    except ValueError as exc:
        return jsonify({
            "error": str(exc)
        }), 400

    except PyMongoError:
        return jsonify({
            "error": "Database operation failed"
        }), 500

    except RuntimeError as exc:
        return jsonify({
            "error": str(exc)
        }), 500

    except Exception as exc:
        print("ERROR IN /ask:", repr(exc))
        return jsonify({
            "error": str(exc)
        }), 502