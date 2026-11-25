from flask import Flask
from app.config import Config
from app.models.models import db
from app.routes.api_routes import api_bp
from app.utils.responses import error_response
from app.utils.seed import seed_database


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(_err):
        return error_response("Endpoint atau resource tidak ditemukan.", 404)

    @app.errorhandler(405)
    def method_not_allowed(_err):
        return error_response("HTTP method tidak diizinkan.", 405)

    @app.errorhandler(500)
    def internal_error(_err):
        db.session.rollback()
        return error_response("Terjadi kesalahan internal pada server.", 500)

    with app.app_context():
        db.create_all()
        if not app.config.get("TESTING"):
            seed_database()

    return app