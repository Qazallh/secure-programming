from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import os
import secrets
from models import db, User, Task
from routes.auth_routes import auth_bp
from routes.task_routes import task_bp
from routes.admin_routes import admin_bp

# Create Flask application
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
app.config["DEBUG"] = False

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_SECURE_COOKIES", "1") == "1"

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(task_bp)
app.register_blueprint(admin_bp)


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('task_bp.dashboard'))
    return redirect(url_for('auth_bp.login'))


# Create database tables
@app.before_request
def create_tables():
    with app.app_context():
        db.create_all()


@app.before_request
def csrf_protect():
    if request.method != "POST":
        return

    token = session.get("csrf_token")
    form_token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    if not token or not form_token or token != form_token:
        abort(400)


@app.context_processor
def inject_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return {"csrf_token": session["csrf_token"]}


@app.after_request
def set_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self'; "
        "style-src-attr 'none'; "
        "script-src-attr 'none'; "
        "img-src 'self' data:; "
        "script-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


if __name__ == "__main__":
    app.run(debug=False)