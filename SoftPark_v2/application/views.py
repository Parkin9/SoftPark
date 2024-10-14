from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
from .models import Worker


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        worker = Worker.query.filter_by(login=login).first()
        if worker:
            if check_password_hash(worker.password, password):
                # A parameter "remember=True" means that a logged in user
                # will be save in cookies (or in session file), on client's computer.
                login_user(worker, remember=False)
                return redirect(url_for('auth.home'))
            else:
                flash("Niepoprawny login i\\lub hasło.", category='error')
        else:
            flash("Niepoprawny login i\\lub hasło.", category='error')

    return render_template('login.html', worker=current_user)
