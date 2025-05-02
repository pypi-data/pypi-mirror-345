from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_realtime_analytics import FlaskRealTimeAnalytics
import os


def test_extension_initialization():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db = SQLAlchemy(app)
    with app.app_context():
        analytics = FlaskRealTimeAnalytics(app, db)
        assert analytics.app is app
        assert analytics.db is db


def test_analytics_route():
    # Set template_folder to absolute path of flask_realtime_analytics/templates/
    template_path = os.path.join(os.path.dirname(__file__), '..', 'flask_realtime_analytics', 'templates')
    app = Flask(__name__, template_folder=template_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db = SQLAlchemy(app)
    with app.app_context():
        analytics = FlaskRealTimeAnalytics(app, db)
        client = app.test_client()
        response = client.get('/analytics')
        assert response.status_code == 200
