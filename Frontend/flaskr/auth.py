# Imports
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
        This method handles the functionalities of the loginsite. It extracts and validates the user id and user type.
        Further it sets the session objects.
        :return: If login succeeds the user gets logged in and redirected to the proper site depending on the order
        status. Else an error message and login site are returned.
    """
    if request.method == 'POST':
        user_id = request.form['order_nr']
        db = get_db()
        error = None
        
        if request.form['option_user'] == "customer":
            user = db.execute(
                'SELECT * FROM orders WHERE id = ? AND order_status != \'completed\'', (user_id,)
                ).fetchone()
        else:
            user = db.execute(
                'SELECT * FROM stations WHERE id = ?', (user_id,)
                ).fetchone()

        if user is None:
            error = 'Invalid input'

        if error is None:
            
            session.clear()

            session['user_type'] = request.form['option_user']
            session['user_id'] = user['id']
            return redirect(url_for('redirection'))

        flash(error, category="error")

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """
        Load the logged-in user's information before each app request.
        This function is a `before_app_request` decorator that runs before each request to the application.
        It checks if a user is logged in based on the session data. If a user is logged in, it retrieves user
        information from the database and sets the `g.user` and `g.user_type` variables, which can be accessed
        throughout the request context.
        :return: None
    """
    user_id = session.get('user_id')
    g.user_type = session.get('user_type')
    if user_id is None:
        g.user = None
    else:

        if g.user_type == "customer":
            g.user = get_db().execute(
                'SELECT * FROM orders WHERE id = ?', (user_id,)
                ).fetchone()
        else:
            g.user = get_db().execute(
                'SELECT * FROM stations WHERE id = ?', (user_id,)
                ).fetchone()


@bp.route('/logout')
def logout():
    """
        This route clears the user's session data using the `session.clear()` function and then redirects the user
        to the login site. This effectively logs the user out of the application.
        :return: Redirect to the loginsite
    """
    session.clear()
    return redirect(url_for('redirection'))


def login_required(user_type):
    """
    This decorator checks if a user is logged in as the correct user type before allowing access to the wrapped view.
    If the user is not logged in or is logged in as a different user type, they are redirected to the login page.
    :param view: The view function to be decorated.
    :return: The decorated view function.
    """
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None or g.user_type != user_type:
                return redirect(url_for('auth.login'))

            return view(**kwargs)

        return wrapped_view

    return decorator
