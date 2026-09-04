import time
from unittest.mock import patch
from pymongo.errors import PyMongoError # type: ignore
from app import create_app
from app.services.ai_service import MockAIService


def create_test_client():
    app = create_app()
    return app.test_client()


def test_valid_batch():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        return_value="Answer: {{userInput}}",
    ), patch(
        "app.routes.ai_routes.generate_responses_async",
        return_value=[
            {"response": "Python answer"},
            {"response": "Flask answer"},
            {"response": "MongoDB answer"},
        ],
    ), patch(
        "app.routes.ai_routes.save_history",
    ):
        response = client.post(
            "/ask/batch",
            json={
                "userInputs": [
                    "What is Python?",
                    "What is Flask?",
                    "What is MongoDB?",
                ]
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert "responses" in data
    assert len(data["responses"]) == 3


def test_empty_batch():
    client = create_test_client()

    response = client.post(
        "/ask/batch",
        json={
            "userInputs": []
        },
    )

    assert response.status_code == 400


def test_missing_user_inputs():
    client = create_test_client()

    response = client.post(
        "/ask/batch",
        json={},
    )

    assert response.status_code == 400


def test_wrong_user_inputs_type():
    client = create_test_client()

    response = client.post(
        "/ask/batch",
        json={
            "userInputs": "What is Python?"
        },
    )

    assert response.status_code == 400


def test_invalid_batch_item():
    client = create_test_client()

    response = client.post(
        "/ask/batch",
        json={
            "userInputs": [
                "What is Python?",
                123,
            ]
        },
    )

    assert response.status_code == 400


def test_batch_response_count():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        return_value="Answer: {{userInput}}",
    ), patch(
        "app.routes.ai_routes.generate_responses_async",
        return_value=[
            {"response": "Answer 1"},
            {"response": "Answer 2"},
            {"response": "Answer 3"},
        ],
    ), patch(
        "app.routes.ai_routes.save_history",
    ):
        response = client.post(
            "/ask/batch",
            json={
                "userInputs": [
                    "A",
                    "B",
                    "C",
                ]
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["responses"]) == 3


def test_batch_response_order():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        return_value="Answer: {{userInput}}",
    ), patch(
        "app.routes.ai_routes.generate_responses_async",
        return_value=[
            {"response": "Response A"},
            {"response": "Response B"},
            {"response": "Response C"},
        ],
    ), patch(
        "app.routes.ai_routes.save_history",
    ):
        response = client.post(
            "/ask/batch",
            json={
                "userInputs": [
                    "A",
                    "B",
                    "C",
                ]
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    returned_inputs = [
        item["userInput"]
        for item in data["responses"]
    ]

    assert returned_inputs == [
        "A",
        "B",
        "C",
    ]


def test_ai_service_preserves_order_with_different_completion_times():
    service = MockAIService()

    delays = {
        "A": 0.30,
        "B": 0.10,
        "C": 0.20,
    }

    def mocked_generate_response(prompt):
        time.sleep(delays[prompt])
        return f"Response {prompt}"

    with patch.object(
        service,
        "generate_response",
        side_effect=mocked_generate_response,
    ):
        responses = service.generate_responses_async(
            ["A", "B", "C"]
        )

    assert responses == [
        {"response": "Response A"},
        {"response": "Response B"},
        {"response": "Response C"},
    ]


def test_batch_ai_failure():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        return_value="Answer: {{userInput}}",
    ), patch(
        "app.routes.ai_routes.generate_responses_async",
        return_value=[
            {"response": "Python answer"},
            {"error": "AI service unavailable"},
            {"response": "MongoDB answer"},
        ],
    ), patch(
        "app.routes.ai_routes.save_history",
    ):
        response = client.post(
            "/ask/batch",
            json={
                "userInputs": [
                    "What is Python?",
                    "What is Flask?",
                    "What is MongoDB?",
                ]
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["responses"][0]["response"] == "Python answer"

    assert data["responses"][1]["error"] == (
        "AI service unavailable"
    )

    assert data["responses"][2]["response"] == "MongoDB answer"


def test_batch_database_failure():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        side_effect=PyMongoError("MongoDB connection failed"),
    ):
        response = client.post(
            "/ask/batch",
            json={
                "userInputs": [
                    "What is Python?",
                    "What is Flask?",
                ]
            },
        )

    assert response.status_code == 500

    assert response.get_json() == {
        "error": "Database service is unavailable"
    }

def test_batch_over_maximum_size():
    client = create_test_client()

    response = client.post(
        "/ask/batch",
        json={
            "userInputs": [
                f"Question {i}"
                for i in range(11)
            ]
        },
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "Maximum batch size is 10"
    }

def test_batch_missing_json_body():
    client = create_test_client()

    response = client.post(
        "/ask/batch",
        data="not valid json",
        content_type="application/json",
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "Request body must be a JSON object"
    }

def test_batch_prompt_not_found():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        side_effect=ValueError(
            "Prompt 'Education_Prompt' not found"
        ),
    ):
        response = client.post(
            "/ask/batch",
            json={
                "userInputs": [
                    "What is Python?"
                ]
            },
        )

    assert response.status_code == 404

    assert response.get_json() == {
        "error": "Prompt 'Education_Prompt' not found"
    }

def test_batch_history_persistence():
    client = create_test_client()

    with patch(
        "app.routes.ai_routes.get_prompt_template",
        return_value="Answer: {{userInput}}",
    ), patch(
        "app.routes.ai_routes.generate_responses_async",
        return_value=[
            {"response": "Python answer"},
            {"response": "Flask answer"},
        ],
    ), patch(
        "app.routes.ai_routes.save_history",
    ) as mock_save_history:

        response = client.post(
            "/ask/batch",
            json={
                "userInputs": [
                    "What is Python?",
                    "What is Flask?",
                ]
            },
        )

    assert response.status_code == 200

    assert mock_save_history.call_count == 2