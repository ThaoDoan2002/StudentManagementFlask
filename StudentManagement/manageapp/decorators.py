from functools import wraps
from flask import request, redirect, url_for, abort
from flask_login import current_user

from manageapp.models import UserRole


def loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index', next=request.url)) #chạy index function
        return f(*args, **kwargs)

    return decorated_function

def teacherlogined(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_role != UserRole.EMPLOYEE:
            return redirect(url_for('index', next=request.url)) #chạy index function
        return f(*args, **kwargs)

    return decorated_function


def employeelogined(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_role != UserRole.TEACHER:
            return redirect(url_for('index', next=request.url)) #chạy index function
        return f(*args, **kwargs)

    return decorated_function


