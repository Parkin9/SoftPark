from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = 'SoftPark_database'


def create_app():
    app = Flask(__name__)
    ''' IMPORTANT!!! Change the secret key below, when GO-LIVE. '''
    app.config['SECRET_KEY'] = 'GSft542968Fjs7689d@%_9852gsJhSA#!g6HJ_!fs32VdC95'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}.sqlite3'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Worker

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'views.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Worker.query.get(int(id))

    return app

# Test settera set_month_fee()
# from .model import Client
# new_client = Client()
# new_client.set_mouth_fee(123.98134623)
# print(new_client)

def create_database(app):
    if not path.exists('application/' + DB_NAME):
        db.create_all(app=app)
        print('Application\'s Database created!')