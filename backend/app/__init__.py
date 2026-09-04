from flask import Flask # type: ignore
from flask_cors import CORS # type: ignore


def create_app():
    app = Flask(__name__)

    CORS(
        app,
        origins=[
            "http://localhost:5173",
        ],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    from app.routes.ai_routes import ai_bp
    app.register_blueprint(ai_bp)

    return app