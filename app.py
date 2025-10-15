from flask import Flask
from config import config
from extensions import init_extensions, db
from routes import api
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    init_extensions(app)

    with app.app_context():
        app.register_blueprint(api)
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if db_path and not os.path.exists(db_path):
            db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
