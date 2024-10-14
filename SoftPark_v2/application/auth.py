from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import exc
import json
from .models import Worker, Client, SmsCode
from . import db


auth = Blueprint('auth', __name__)


@auth.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    ''' Presentation of all existing clients. '''
    clients = Client.query.all()

    ''' Adding a new client. '''
    if request.method == 'POST':
        name = request.form.get('name').strip()
        phone_nr = request.form.get('phone_nr').replace(' ', '')
        month_fee = request.form.get('month_fee')
        contract_start = request.form.get('contract_start')

        client = Client.query.filter_by(phone_nr=phone_nr).first()

        if client:
            flash("Klient o podanym NR TELEFONU istnieje już w Systemie.", category='error')
        elif len(name) < 3:
            flash("NAZWA KLIENTA musi zawierać co najmniej 3 znaki.", category='error')
        elif not phone_nr.isdecimal() or len(phone_nr) != 9:
            flash("NUMER TELEFONU musi zawierać wyłącznie 9 cyfr. ", category='error')
        elif month_fee == 0.00:
            flash("ABONAMENT nie może wynosić 0 PLN.", category='error')
        else:
            try:
                new_client = Client(name=name
                                    , phone_nr=phone_nr
                                    , month_fee=month_fee
                                    , contract_start=contract_start)
                db.session.add(new_client)
                db.session.commit()
                flash(f"Pomyślnie dodano klienta: {new_client.name}", category='success')
                return redirect(url_for('auth.home'))
            except exc.IntegrityError:
                db.session.rollback()
                flash(f"Nie powiodło się dodawanie klienta: {new_client.name}. "
                        + "Trzeba dzwonić do Piotrka."
                        , category='error')
                return redirect(url_for('auth.home'))

    return render_template('home.html', worker=current_user, clients=clients)


@auth.route('/update-client', methods=['POST'])
@login_required
def update_client():
    ''' Getting an updated date about the client. '''
    client_id = request.form.get('client_id')
    name = request.form.get('name').strip()
    phone_nr = request.form.get('phone_nr').replace(' ', '')
    month_fee = request.form.get('month_fee')
    contract_start = request.form.get('contract_start')

    ''' Input date validation. '''
    if len(name) < 3:
        flash("NAZWA KLIENTA musi zawierać co najmniej 3 znaki.", category='error')
    elif not phone_nr.isdecimal() or len(phone_nr) != 9:
        flash("NUMER TELEFONU musi zawierać wyłącznie 9 cyfr. ", category='error')
    elif month_fee == 0.00:
        flash("ABONAMENT nie może wynosić 0 PLN.", category='error')
    else:
        ''' Updating client's date in DB. '''
        try:
            updated_client = Client.query.get(client_id)
            updated_client.name = name
            updated_client.phone_nr = phone_nr
            updated_client.set_month_fee(month_fee)
            updated_client.set_contract_start(contract_start)

            db.session.commit()
            flash(f"Pomyślnie zaktualizowano klienta: {updated_client.name}", category='success')

        except exc.IntegrityError:
            db.session.rollback()
            flash(f"Nie powiodła się aktualizacja klienta: {updated_client.name}. "
                    + "Trzeba niestety dzwonić do Piotrka."
                    , category='error')
            
    return redirect(url_for('auth.home'))


@auth.route('/delete-client', methods=['POST'])
@login_required
def delete_client():
    client = json.loads(request.data)
    clientId = client['clientId']
    client = Client.query.get(clientId)
    
    if client:
        db.session.delete(client)
        db.session.commit()
        flash(f"Pomyślnie usunięto klienta: {client.name}", category='success')
    
    return jsonify({})


@auth.route('/sms-codes', methods=['GET','POST'])
@login_required
def sms_codes():
    sms_codes = SmsCode.query.all()

    return render_template('sms_codes.html', worker=current_user, sms_codes=sms_codes)

@auth.route('/add-worker', methods=['GET', 'POST'])
@login_required
def add_worker():
    if request.method == 'POST':
        login = request.form.get('login').strip()
        first_name = request.form.get('first_name').strip()
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        worker = Worker.query.filter_by(login=login).first()
        
        if worker:
            flash("Podany LOGIN istnieje już w Systemie.", category='error')
        elif len(login) < 4:
            flash("LOGIN musi zawierać co najmniej 4 znaki.", category='error')
        elif len(first_name) < 2:
            flash("IMIĘ musi zawierać co najmniej 2 znaki.", category='error')
        elif password1 != password2:
            flash("Podane HASŁA nie pasują do siebie.", category='error')
        elif len(password1) < 8:
            flash("HASŁO musi zawierać co najmniej 8 znaków.", category='error')
        else:
            try:
                new_worker = Worker(login=login
                                    , first_name=first_name
                                    , password=generate_password_hash(password1, method='pbkdf2:sha256'))
                db.session.add(new_worker)
                db.session.commit()
                flash(f"Pomyślnie dodano pracownika: {new_worker.first_name}", category='success')
                return redirect(url_for('auth.home'))
            except:
                flash(f"Nie powiodło się dodawanie pracownika: {new_worker.first_name}. "
                        + "Trzeba niestety dzwonić do Piotrka.", category='error')
                return redirect(url_for('auth.add_worker'))

    return render_template('add_worker.html', worker=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    # return redirect(url_for('views.login'))
    return render_template('login.html', worker=current_user)
