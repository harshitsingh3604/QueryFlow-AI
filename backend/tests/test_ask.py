from unittest.mock import patch
from pymongo.errors import PyMongoError # type: ignore
from app import create_app


def create_test_client():
    app = create_app()
    return app.test_client()


def test_ask_valid_request():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        return_value="You are an expert. Answer: {{userInput}}",
    ), patch(
        "app.routes.ai_routes.generate_response",
        return_value="Mocked AI response",
    ), patch(
        "app.routes.ai_routes.save_history",
    ):
        response = client.post(
            "/ask",
            json={
                "userInput": "How much should I score in each subject to pass CA final?"
            },
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "response": "Mocked AI response"
    }


def test_ask_missing_user_input():
    client = create_test_client()

    response = client.post(
        "/ask",
        json={},
    )

    assert response.status_code == 400


def test_ask_empty_user_input():
    client = create_test_client()

    response = client.post(
        "/ask",
        json={
            "userInput": "",
        },
    )

    assert response.status_code == 400


def test_ask_wrong_user_input_type():
    client = create_test_client()

    response = client.post(
        "/ask",
        json={
            "userInput": 123,
        },
    )

    assert response.status_code == 400


def test_ask_ai_failure():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        return_value="You are an expert. Answer: {{userInput}}",
    ), patch(
        "app.routes.ai_routes.generate_response",
        side_effect=Exception("AI service unavailable"),
    ):
        response = client.post(
            "/ask",
            json={
                "userInput": "What is Java?"
            },
        )

    assert response.status_code == 502
    assert response.get_json() == {
        "error": "AI service is unavailable"
    }


def test_ask_database_failure():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        side_effect=PyMongoError("MongoDB connection failed"),
    ):
        response = client.post(
            "/ask",
            json={
                "userInput": "What is Python?"
            },
        )

    assert response.status_code == 500

    assert response.get_json() == {
        "error": "Database service is unavailable"
    }