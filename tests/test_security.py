import os
import sys
import tempfile

import pytest
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app as flask_app
from models import db, User, Task


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()

    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY="test-secret",
    )

    # Remove only the auto-create tables hook while keeping CSRF protection.
    for blueprint, funcs in list(flask_app.before_request_funcs.items()):
        flask_app.before_request_funcs[blueprint] = [
            func for func in funcs if func.__name__ != "create_tables"
        ]

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


def create_user(username, password, is_admin=False):
    user = User(username=username, password="", is_admin=is_admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def get_csrf_token(response):
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
    assert match is not None
    return match.group(1)


def login(client, username, password):
    csrf_response = client.get("/login")
    token = get_csrf_token(csrf_response)
    return client.post(
        "/login",
        data={"username": username, "password": password, "csrf_token": token},
        follow_redirects=False,
    )


def test_admin_dashboard_requires_admin(client, app):
    with app.app_context():
        create_user("employee", "password123", is_admin=False)

    login(client, "employee", "password123")
    response = client.get("/admin/dashboard", follow_redirects=False)

    assert response.status_code == 403


def test_admin_dashboard_allows_admin(client, app):
    with app.app_context():
        create_user("admin", "adminpass", is_admin=True)

    login(client, "admin", "adminpass")
    response = client.get("/admin/dashboard", follow_redirects=False)

    assert response.status_code == 200


def test_delete_user_requires_admin(client, app):
    with app.app_context():
        employee = create_user("employee", "password123", is_admin=False)
        victim = create_user("victim", "password123", is_admin=False)
        victim_id = victim.id

    login(client, "employee", "password123")
    csrf_response = client.get("/task/create")
    token = get_csrf_token(csrf_response)
    response = client.post(
        f"/admin/delete_user/{victim_id}",
        data={"csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_update_task_requires_owner(client, app):
    with app.app_context():
        owner = create_user("owner", "password123", is_admin=False)
        other = create_user("other", "password123", is_admin=False)
        task = Task(title="Task 1", description="Desc", user_id=owner.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    login(client, "other", "password123")
    csrf_response = client.get("/task/create")
    token = get_csrf_token(csrf_response)
    response = client.post(
        f"/task/update/{task_id}",
        data={"title": "New", "description": "Changed", "csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_registration_hashes_password(client, app):
    csrf_response = client.get("/register")
    token = get_csrf_token(csrf_response)
    response = client.post(
        "/register",
        data={"username": "newuser", "password": "Passw0rd!", "csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code in (302, 200)

    with app.app_context():
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.password != "Passw0rd!"


def test_csrf_protects_create_task(client, app):
    with app.app_context():
        create_user("employee", "password123", is_admin=False)

    login(client, "employee", "password123")
    response = client.post(
        "/task/create",
        data={"title": "Task", "description": "Desc"},
        follow_redirects=False,
    )

    assert response.status_code == 400
