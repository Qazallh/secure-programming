from functools import wraps

from flask import session, redirect, url_for, abort


def login_required(view_func):
	@wraps(view_func)
	def wrapped(*args, **kwargs):
		if "user_id" not in session:
			return redirect(url_for("auth_bp.login"))
		return view_func(*args, **kwargs)

	return wrapped


def admin_required(view_func):
	@wraps(view_func)
	def wrapped(*args, **kwargs):
		if "user_id" not in session:
			return redirect(url_for("auth_bp.login"))
		if not session.get("is_admin"):
			abort(403)
		return view_func(*args, **kwargs)

	return wrapped
