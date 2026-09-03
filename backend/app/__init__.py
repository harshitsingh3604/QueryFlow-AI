from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    from app.routes.ai_routes import ai_bp

    app.register_blueprint(ai_bp)

    return app